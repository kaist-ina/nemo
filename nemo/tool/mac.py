def count_mac_for_nas_s(model_name, height, width):
    if height == 240 and width == 426:
        if model_name == 'NAS_S_B8_F9_S4_deconv':
            return 3552 * 1000 * 1000
        elif model_name == 'NAS_S_B8_F21_S4_deconv':
            return 31555 * 1000 * 1000
        elif model_name == 'NAS_S_B8_F32_S4_deconv':
            return 101274 * 1000 * 1000
        elif model_name == 'NAS_S_B8_F48_S4_deconv':
            return 320966 * 1000 * 1000
        else:
            return None

    else:
        return None

def count_mac_for_nemo_s(model_name, height, width):
    if height == 240 and width == 426:
        if model_name == 'NEMO_S_B8_F4_S4_deconv':
            return 384 * 1000 * 1000
        elif model_name == 'NEMO_S_B8_F9_S4_deconv':
            return 1913 * 1000 * 1000
        elif model_name == 'NEMO_S_B8_F21_S4_deconv':
            return 10337 * 1000 * 1000
        elif model_name == 'NEMO_S_B8_F32_S4_deconv':
            return 23958 * 1000 * 1000
        elif model_name == 'NEMO_S_B8_F48_S4_deconv':
            return 53846 * 1000 * 1000 #TODO: needed tob updated excluding bilinear
        else:
            return None
    #TODO: needed tob updated excluding bilinear
    if height == 360 and width == 640:
        if model_name == 'NEMO_S_B8_F8_S3_deconv':
            return 3411 * 1000 * 1000
        elif model_name == 'NEMO_S_B8_F18_S3_deconv':
            return 17132 * 1000 * 1000
        elif model_name == 'NEMO_S_B8_F29_S3_deconv':
            return 44359 * 1000 * 1000
        elif model_name == 'NEMO_S_B8_F42_S3_deconv':
            return 92926 * 1000 * 1000
        else:
            return None
    #TODO: needed tob updated excluding bilinear
    if height == 480 and width == 854:
        if model_name == 'NEMO_S_B8_F4_S2_deconv':
            return 1539 * 1000 * 1000
        elif model_name == 'NEMO_S_B8_F9_S2_deconv':
            return 7676 * 1000 * 1000
        elif model_name == 'NEMO_S_B8_F18_S2_deconv':
            return 30487 * 1000 * 1000
        elif model_name == 'NEMO_S_B8_F26_S2_deconv':
            return 63474 * 1000 * 1000
        else:
            return None
    else:
        return None

def count_mac_for_dnn(model_name, height, width):
    if model_name.startswith('NAS_S'):
        return count_mac_for_nas_s(model_name, height, width)
    elif model_name.startswith('NEMO_S'):
        return count_mac_for_nemo_s(model_name, height, width)
    else:
        return None

def count_mac_for_cache(height, width, channel):
    return width * height * channel * 8
