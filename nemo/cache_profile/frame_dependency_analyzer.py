import os
import sys
import argparse
import collections

import numpy as np
import networkx as nx

from nemo.tool.video import profile_video
import nemo.dnn.model

class FDA():
    def __init__(self, log_dir):
        self.log_dir = log_dir

    def node_name(self, frame_index, node_index_dict):
        node_name = '{}.{}'.format(frame_index[0], frame_index[1])
        return node_name

    #Caution: Need to run NEMO first to prepare 'metdata.txt' by 'online_cache_latency.py'
    def all(self):
        metadata_log_path = os.path.join(self.log_dir, 'metadata.txt')
        print(metadata_log_path)
        assert(os.path.exists(metadata_log_path))

        #node index
        node_index_dict = {}
        count = 0
        with open(metadata_log_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip().split('\t')
                video_frame = int(line[0])
                super_frame = int(line[1])
                node_index_dict[(video_frame, super_frame)] = count
                count += 1

        #build a DAG
        G = nx.DiGraph()
        with open(metadata_log_path, 'r') as f:
            lines = f.readlines()
            for idx, line in enumerate(lines):
                result = line.strip().split('\t')
                video_frame = int(result[0])
                super_frame = int(result[1])
                frame_type = result[-1]
                is_anchor_point = int(result[2])
                node_name = self.node_name((video_frame, super_frame), node_index_dict)

                if len(result) == 12:
                    #add node
                    G.add_node(node_name, video_frame=video_frame, super_frame=super_frame, frame_type=frame_type, is_anchor_point=is_anchor_point)

                    #add edge
                    for i in range(3):
                        ref_video_frame = int(result[2*i+5])
                        ref_super_frame = int(result[2*i+6])
                        ref_node_name = self.node_name((ref_video_frame, ref_super_frame), node_index_dict)
                        G.add_edge(ref_node_name, node_name)
                else:
                    #add node
                    G.add_node(node_name, video_frame=video_frame, super_frame=super_frame, frame_type=frame_type, is_anchor_point=is_anchor_point)

        #log: reference counts of anchor points
        out_degree = []
        nodes = sorted(G.nodes, key=lambda x: float(x))
        for node in nodes:
            if G.nodes[node]['is_anchor_point'] == 1:
                out_degree.append(G.out_degree(node))
        out_degree.sort()
        count = {x:out_degree.count(x) for x in out_degree}
        value, count = list(count.keys()), list(count.values())
        print('average is {}'.format(np.average(out_degree)))
        cdf = []
        for i in range(len(count)):
            cdf.append(sum(count[0:i+1]) / sum(count))

        cdf_log_path = os.path.join(self.log_dir, 'anchor_point_reference_count_cdf.txt')
        is_first = True
        with open(cdf_log_path, 'w') as f:
            for x_val, y_val in zip(value, cdf):
                if is_first:
                    if x_val != 0:
                        f.write('{}\t{}\n'.format(0, 0))
                        f.write('{}\t{}\n'.format(x_val, 0))
                        f.write('{}\t{}\n'.format(x_val, y_val))
                    else:
                        f.write('{}\t{}\n'.format(x_val, 0))
                        f.write('{}\t{}\n'.format(x_val, y_val))
                    is_first = False
                else:
                    f.write('{}\t{}\n'.format(x_val, y_pre_val))
                    f.write('{}\t{}\n'.format(x_val, y_val))
                y_pre_val = y_val

        #log: reference counts of frames
        out_degree = []
        nodes = sorted(G.nodes, key=lambda x: float(x))
        for node in nodes:
            out_degree.append(G.out_degree(node))
        out_degree.sort()
        count = {x:out_degree.count(x) for x in out_degree}
        value, count = list(count.keys()), list(count.values())
        cdf = []
        for i in range(len(count)):
            cdf.append(sum(count[0:i+1]) / sum(count))

        cdf_log_path = os.path.join(self.log_dir, 'frame_reference_count_cdf.txt')
        is_first = True
        with open(cdf_log_path, 'w') as f:
            for x_val, y_val in zip(value, cdf):
                if is_first:
                    if x_val != 0:
                        f.write('{}\t{}\n'.format(0, 0))
                        f.write('{}\t{}\n'.format(x_val, 0))
                        f.write('{}\t{}\n'.format(x_val, y_val))
                    else:
                        f.write('{}\t{}\n'.format(x_val, 0))
                        f.write('{}\t{}\n'.format(x_val, y_val))
                    is_first = False
                else:
                    f.write('{}\t{}\n'.format(x_val, y_pre_val))
                    f.write('{}\t{}\n'.format(x_val, y_val))
                y_pre_val = y_val

        #log: frame types of anchor points
        key_frame = []
        alternative_reference_frame = []
        golden_frame = []
        normal_frame = []
        nodes = sorted(G.nodes, key=lambda x: float(x))
        for node in nodes:
            #print(node, G.out_degree(node), list(G.successors(node)))
            if G.nodes[node]['is_anchor_point'] == 1:
                if G.nodes[node]['frame_type'] == 'key_frame':
                    key_frame.append(G.out_degree(node))
                elif G.nodes[node]['frame_type'] == 'alternative_reference_frame':
                    alternative_reference_frame.append(G.out_degree(node))
                elif G.nodes[node]['frame_type'] == 'normal_frame':
                    if G.out_degree(node) > 1:
                        golden_frame.append(G.out_degree(node))
                    else:
                        normal_frame.append(G.out_degree(node))
                else:
                    print(G.nodes[node]['frame_type'])
                    raise NotImplementedError

        total_num = len(key_frame) + len(alternative_reference_frame) + len(golden_frame) + len(normal_frame)
        frame_type_log = os.path.join(self.log_dir, 'anchor_point_frame_type.txt')
        with open(frame_type_log, 'w') as f:
            f.write('Key\t{:.2f}\n'.format(len(key_frame)/total_num))
            f.write('Alf_ref\t{:.2f}\n'.format(len(alternative_reference_frame)/total_num))
            f.write('Golden\t{:.2f}\n'.format(len(golden_frame)/total_num))
            f.write('Others\t{:.2f}\n'.format(len(normal_frame)/total_num))

        #log: frame types of all frames
        key_frame = []
        alternative_reference_frame = []
        golden_frame = []
        normal_frame = []
        nodes = sorted(G.nodes, key=lambda x: float(x))
        for node in nodes:
            #print(node, G.out_degree(node), list(G.successors(node)))
            if G.nodes[node]['frame_type'] == 'key_frame':
                key_frame.append(G.out_degree(node))
            elif G.nodes[node]['frame_type'] == 'alternative_reference_frame':
                alternative_reference_frame.append(G.out_degree(node))
            elif G.nodes[node]['frame_type'] == 'normal_frame':
                if G.out_degree(node) > 1:
                    golden_frame.append(G.out_degree(node))
                else:
                    normal_frame.append(G.out_degree(node))
            else:
                print(G.nodes[node]['frame_type'])
                raise NotImplementedError

        frame_type_log_path = os.path.join(self.log_dir, 'frame_type.txt')
        with open(frame_type_log_path, 'w') as f:
            f.write("Key frame\t{:.2f}\t{:.2f}\n".format(len(key_frame)/len(nodes) * 100, np.average(key_frame)))
            f.write("Alternative reference frame\t{:.2f}\t{:.2f}\n".format(len(alternative_reference_frame)/len(nodes) * 100, np.average(alternative_reference_frame)))
            f.write("Golden frame\t{:.2f}\t{:.2f}\n".format(len(golden_frame)/len(nodes) * 100, np.average(golden_frame)))
            f.write("Normal frame\t{:.2f}\t{:.2f}\n".format(len(normal_frame)/len(nodes) * 100, np.average(normal_frame)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Frame Dependency Analyzer')

    #options for libvpx
    parser.add_argument('--data_dir', type=str, required=True)
    parser.add_argument('--content', type=str, required=True)
    parser.add_argument('--video_name', type=str, required=True)

    #dnn
    parser.add_argument('--model_type', type=str, default='nemo_s')
    parser.add_argument('--num_filters', type=int, default=None)
    parser.add_argument('--num_blocks', type=int, default=None)
    parser.add_argument('--upsample_type', type=str, default='deconv')
    parser.add_argument('--train_type', type=str, default='finetune_video')

    #anchor point selector
    parser.add_argument('--algorithm', default=None)

    #codec
    parser.add_argument('--output_width', type=int, default=1920)
    parser.add_argument('--output_height', type=int, default=1080)

    #frame_depednecny_analyzer
    parser.add_argument('--decode_mode', required=True)

    args = parser.parse_args()

    #profile videos
    data_dir = os.path.join(args.data_dir, args.content)
    video_path = os.path.join(data_dir, 'video', args.video_name)
    video_profile = profile_video(video_path)
    scale = args.output_height // video_profile['height']
    nhwc = [1, video_profile['height'], video_profile['width'], 3]

    #run fda
    if args.decode_mode == 'decode':
        log_dir = os.path.join(args.data_dir, args.content, 'log', args.video_name)
    elif args.decode_mode == 'decode_sr':
        assert(args.num_filters is not None and args.num_blocks is not None)
        model = nemo.dnn.model.build(args.model_type, args.num_blocks, args.num_filters, scale, args.upsample_type)
        log_dir = os.path.join(args.data_dir, args.content, 'log', args.video_name, model.name)
    elif args.decode_mode == 'decode_cache':
        assert(args.num_filters is not None and args.num_blocks is not None)
        assert(args.algorithm is not None)
        model = nemo.dnn.model.build(args.model_type, args.num_blocks, args.num_filters, scale, args.upsample_type)
        log_dir = os.path.join(args.data_dir, args.content, 'log', args.video_name, model.name, args.algorithm)
        pass
    else:
        raise NotImplementedError

    fda = FDA(log_dir)
    fda.all()
