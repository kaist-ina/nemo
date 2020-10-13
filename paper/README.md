## 1. DNN Specifications (cited in Section 5.3, "Providing multiple options")

NEMO uses multiple quality DNNs (Low, Medium, High) whose architecture is described in the below figure.

Each residual block consists of two convolution layer, one ReLU layer, and one element-wise summation layer (e.g., Conv-ReLU-Conv-Sum)

<img src="https://user-images.githubusercontent.com/62630456/77510739-cb2a4300-6eb2-11ea-8ae0-2795939b4c8f.png" width="90%"></img>

The below table specifies the numbers of residual blocks and the number of channels of convolution layers for each quality DNN.

|  Resolution   | Quality | Number of residual blocks | Number of channels |
|:-------------:|:-------------:|:-------------:|:-----:|
| 240p      | Low      | 4 | 9 |
| 240p      | Medium      | 8 | 21 |
| 240p      | High      | 8 | 32 |
| 360p      | Low      | 4 | 8 |
| 360p      | Medium      | 4 | 18 |
| 360p      | High      | 4 | 29 |
| 480p      | Low      | 4 | 4 |
| 480p      | Medium      | 4 | 9 |
| 480p      | High      | 4 | 18 |

## 2. DNN quality to Device Mapping (cited in Section 7, "Baseline")

NEMO selects different quality DNNs depending on videos and devices (refer Section 5.3, "Adapting to Devices and Contents").

The below table desribes the mapping from DNN qualities to our local mobile devices including Xiaomi Redmi Note 7 (Entry-level), Xiaomi Mi9 (High-end), and LG Gpad5 (Tablet).

### a. 240p to 1080p

|  Content  | Xiaomi Redmi Note7 | Xiaomi Mi9 | LG Gpad 5 |
|:-------------:|:-------------:|:-------------:|:-----:|
| product_review | Low, Low, Low | High, High, High | Low, Low, Low |
| how_to | Low, Low, Low | High, High, High | Low, Low, Low |
| vlogs | Low, Low, Low | Medium, High, Medium | Low, Low, Low |
| game_play | Low, Low, Low | Medium, High, Medium | Low, Low, Low |
| skit | Low, Low, Low | Medium, Medium, High | Low, Low, Low |
| haul | Low, Low, Low | Medium, High, High | Low, Low, Low |
| challenge | Low, Low, Low | High, High, High | Low, Low, Low |
| favorite | Low, Low, Low | Medium, High, High | Low, Low, Medium |
| education | Low, Low, Low | High, Medium, High | Medium, Low, Low |
| unboxing | Low, Low, Low | High, High, High | Low, Low, Low |

### b. 360p to 1080p

|  Content  | Xiaomi Redmi Note7 | Xiaomi Mi9 | LG Gpad 5 | 
|:-------------:|:-------------:|:-------------:|:-----:|
| product_review | Low, Low, Low | Medium, Medium, Medium | Low, Low, Low |
| how_to | Low, Low, Low | Medium, Medium, Medium | Low, Low, Low |
| vlogs | Low, Low, Low | Low, High, Low | Low, Medium, Low |
| game_play | Low, Low, Low | Low, Low, Low | Low, Low, Low |
| skit | Low, Low, Low | Low, Medium, Medium | Low, Low, Low |
| haul | Low, Low, Low | Low, Medium, Medium | Low, Low, Low |
| challenge | Low, Low, Low | Medium, Medium, Medium | Low, Low, Low |
| favorite | Low, Low, Low | Low, Medium, Medium | Low, Low, Low |
| education | Low, Low, Low | High, Low, Medium | Low, Low, Low |
| unboxing | Low, Low, Low | Medium, Medium, Medium | Low, Low, Low |

### c. 480p to 1080p

|  Content  | Xiaomi Redmi Note7 | Xiaomi Mi9 | LG Gpad 5 | 
|:-------------:|:-------------:|:-------------:|:-----:|
| product_review | Low, Low, Medium | Medium, Medium, High | Low, Low, Medium |
| how_to | Low, Low, Low | Medium, Medium, Medium | Medium, Low, Low |
| vlogs | Low, Low, Low | Medium, High, Medium | Low, Medium, Low |
| game_play | Low, Low, Low | Medium, Medium, Medium | Low, Low, Low |
| skit | Low, Low, Low | Medium, Medium, Medium | Low, Low, Low |
| haul | Low, Low, Low | Medium, Medium, Medium | Low, Low, Low |
| challenge | Low, Low, Low | High, High, High | Low, Medium, Medium |
| favorite | Low, Low, Low | Medium, High, High | Low, Medium, Low |
| education | Low, Low, Low | High, Medium, High | Low, Low, Medium |
| unboxing | Low, Low, Low | Medium, Medium, Medium | Low, Low, Low |

## 3. Dataset (Video, Network traces)

NEMO uses two types of datasets: 1) Video to train super-resolution DNNs, 2) Network traces to test adaptive streaming.
We provide them at `dataset`.

## 4. Demo videos

NEMO significantly improves video quality by super-resolution. 

To demonstrate this, we provide three sample videos at `demo`.

## 5. Experiment setting for power measurement

A recent smartphone is equipped an integrated battery.
Thus, we dissebled a smartphone and replaced its battery with the Monsoon power monitor as below image.

<img src="https://user-images.githubusercontent.com/62630456/89301846-15af9d80-d6a5-11ea-88cd-50b993a7d844.jpg" width="90%"></img>
