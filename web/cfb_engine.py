# -*- coding: utf-8 -*-
"""CFB Season Model engine. Built with Claude, 2026 season.
Run weekly:  CFBD_API_KEY=xxxx python cfb_engine.py --week 5 --prev CFB_Season_Model_wk4.xlsx
"""
import json
CONSTS=json.loads(r'''{"A": [59.99711444, 2.83872419], "C": [-28.55350524, 0.24919657, 0.49944732, 23.62678653], "CO": [0.19615430026693625, 0.3499922569957513, 0.030439353935759108, 0.0016185934009142508], "CD": [0.37471325831044666, -0.022274395826206606, -0.002158035489480556], "GRID": [0.0, 0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14, 0.16, 0.18, 0.2, 0.22, 0.24, 0.26, 0.28, 0.3, 0.32, 0.34, 0.36, 0.38, 0.4, 0.42, 0.44, 0.46, 0.48, 0.5, 0.52, 0.54, 0.56, 0.58, 0.6, 0.62, 0.64, 0.66, 0.68, 0.7, 0.72, 0.74, 0.76, 0.78, 0.8, 0.82, 0.84, 0.86, 0.88, 0.9, 0.92, 0.94, 0.96, 0.98, 1.0, 1.02, 1.04, 1.06, 1.08, 1.1, 1.12, 1.14, 1.16, 1.18, 1.2, 1.22, 1.24, 1.26, 1.28, 1.3, 1.32, 1.34, 1.36, 1.38, 1.4, 1.42, 1.44, 1.46, 1.48, 1.5, 1.52, 1.54, 1.56, 1.58, 1.6, 1.62, 1.64, 1.66, 1.68, 1.7, 1.72, 1.74, 1.76, 1.78, 1.8, 1.82, 1.84, 1.86, 1.88, 1.9, 1.92, 1.94, 1.96, 1.98, 2.0, 2.02, 2.04, 2.06, 2.08, 2.1, 2.12, 2.14, 2.16, 2.18, 2.2, 2.22, 2.24, 2.26, 2.28, 2.3, 2.32, 2.34, 2.36, 2.38, 2.4, 2.42, 2.44, 2.46, 2.48, 2.5, 2.52, 2.54, 2.56, 2.58, 2.6, 2.62, 2.64, 2.66, 2.68, 2.7, 2.72, 2.74, 2.76, 2.78, 2.8, 2.82, 2.84, 2.86, 2.88, 2.9, 2.92, 2.94, 2.96, 2.98, 3.0], "DIST": {"PassAtt": [0.997, 0.997, 0.997, 0.994, 0.989, 0.986, 0.9799, 0.9779, 0.9739, 0.9719, 0.9689, 0.9649, 0.9639, 0.9619, 0.9609, 0.9579, 0.9559, 0.9509, 0.9488, 0.9468, 0.9438, 0.9438, 0.9398, 0.9348, 0.9308, 0.9288, 0.9248, 0.9198, 0.9127, 0.9057, 0.8977, 0.8837, 0.8736, 0.8666, 0.8495, 0.8335, 0.8205, 0.8084, 0.7914, 0.7723, 0.7442, 0.7252, 0.7021, 0.6841, 0.66, 0.6479, 0.6179, 0.5888, 0.5657, 0.5436, 0.5145, 0.4945, 0.4754, 0.4624, 0.4383, 0.4102, 0.3882, 0.3651, 0.347, 0.336, 0.317, 0.2959, 0.2798, 0.2628, 0.2437, 0.2257, 0.2066, 0.1876, 0.1805, 0.1705, 0.1545, 0.1434, 0.1304, 0.1234, 0.1123, 0.1073, 0.0983, 0.0933, 0.0893, 0.0863, 0.0812, 0.0782, 0.0712, 0.0682, 0.0672, 0.0642, 0.0602, 0.0562, 0.0542, 0.0522, 0.0471, 0.0421, 0.0401, 0.0351, 0.0331, 0.0321, 0.0291, 0.0261, 0.0251, 0.0241, 0.0211, 0.0201, 0.0191, 0.0181, 0.016, 0.015, 0.014, 0.014, 0.014, 0.013, 0.012, 0.012, 0.012, 0.011, 0.01, 0.01, 0.01, 0.009, 0.009, 0.009, 0.009, 0.009, 0.009, 0.008, 0.008, 0.007, 0.006, 0.006, 0.006, 0.005, 0.005, 0.005, 0.005, 0.004, 0.004, 0.004, 0.004, 0.004, 0.003, 0.003, 0.002, 0.002, 0.002, 0.002, 0.002, 0.002, 0.002, 0.002, 0.002, 0.002, 0.002], "PassCmp": [0.9888, 0.9888, 0.9888, 0.9868, 0.9838, 0.9807, 0.9777, 0.9756, 0.9736, 0.9706, 0.9685, 0.9624, 0.9604, 0.9574, 0.9553, 0.9533, 0.9482, 0.9462, 0.9431, 0.9411, 0.9381, 0.933, 0.9289, 0.9218, 0.9157, 0.9076, 0.9015, 0.8904, 0.8792, 0.8701, 0.8589, 0.8538, 0.8487, 0.8386, 0.8244, 0.8091, 0.7929, 0.7635, 0.7492, 0.731, 0.7117, 0.6914, 0.668, 0.6396, 0.6213, 0.599, 0.5777, 0.5553, 0.536, 0.5107, 0.4893, 0.466, 0.4335, 0.4173, 0.4, 0.3838, 0.3533, 0.336, 0.3289, 0.3127, 0.2944, 0.2772, 0.265, 0.2487, 0.2355, 0.2213, 0.2041, 0.1919, 0.1827, 0.1716, 0.1594, 0.1482, 0.1381, 0.1289, 0.1208, 0.1137, 0.1086, 0.1036, 0.0924, 0.0863, 0.0802, 0.069, 0.065, 0.064, 0.0599, 0.0569, 0.0538, 0.0508, 0.0497, 0.0477, 0.0437, 0.0376, 0.0335, 0.0315, 0.0315, 0.0315, 0.0274, 0.0254, 0.0234, 0.0234, 0.0234, 0.0234, 0.0223, 0.0223, 0.0213, 0.0193, 0.0183, 0.0173, 0.0173, 0.0162, 0.0162, 0.0152, 0.0132, 0.0122, 0.0112, 0.0112, 0.0112, 0.0112, 0.0102, 0.0102, 0.0102, 0.0102, 0.0102, 0.0091, 0.0081, 0.0081, 0.0081, 0.0061, 0.0051, 0.0041, 0.0041, 0.0041, 0.0041, 0.0041, 0.0041, 0.003, 0.003, 0.003, 0.003, 0.003, 0.003, 0.003, 0.003, 0.003, 0.003, 0.003, 0.003, 0.003, 0.003, 0.003, 0.003], "PassRushYds": [0.9937, 0.9916, 0.9874, 0.9874, 0.9863, 0.9832, 0.98, 0.9737, 0.9695, 0.9684, 0.9653, 0.9611, 0.9589, 0.9579, 0.9547, 0.9516, 0.9495, 0.9453, 0.94, 0.9358, 0.9284, 0.9221, 0.9179, 0.9126, 0.9, 0.8916, 0.8811, 0.8758, 0.8642, 0.8579, 0.8474, 0.8358, 0.8263, 0.8095, 0.8, 0.7832, 0.7674, 0.7505, 0.7337, 0.7158, 0.6979, 0.6853, 0.6695, 0.6537, 0.6411, 0.6147, 0.5947, 0.5705, 0.5516, 0.5316, 0.5137, 0.4947, 0.4653, 0.4453, 0.4263, 0.4168, 0.3884, 0.3684, 0.3495, 0.3316, 0.3137, 0.2947, 0.2747, 0.2621, 0.2432, 0.2274, 0.2105, 0.2032, 0.1916, 0.18, 0.1737, 0.1632, 0.1526, 0.1368, 0.1284, 0.1211, 0.1105, 0.1053, 0.1032, 0.0968, 0.0874, 0.0853, 0.0779, 0.0726, 0.0695, 0.0674, 0.0642, 0.0611, 0.0558, 0.0516, 0.0495, 0.0442, 0.0389, 0.0368, 0.0316, 0.0305, 0.0253, 0.0242, 0.0232, 0.0221, 0.0221, 0.0221, 0.02, 0.0168, 0.0137, 0.0137, 0.0126, 0.0126, 0.0105, 0.0095, 0.0074, 0.0074, 0.0063, 0.0063, 0.0063, 0.0042, 0.0042, 0.0032, 0.0032, 0.0032, 0.0032, 0.0032, 0.0021, 0.0021, 0.0021, 0.0021, 0.0021, 0.0021, 0.0021, 0.0021, 0.0021, 0.0011, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "PassTD": [0.7435, 0.7435, 0.7435, 0.7435, 0.7435, 0.7435, 0.7435, 0.7435, 0.7435, 0.7435, 0.7435, 0.7435, 0.7435, 0.7435, 0.7435, 0.7435, 0.7435, 0.7413, 0.7402, 0.739, 0.7357, 0.7323, 0.7255, 0.7199, 0.712, 0.7053, 0.6952, 0.6907, 0.6783, 0.6704, 0.667, 0.6603, 0.6513, 0.6434, 0.6288, 0.6175, 0.604, 0.5951, 0.5906, 0.5771, 0.5647, 0.5546, 0.5467, 0.5377, 0.5309, 0.5163, 0.5107, 0.5028, 0.4972, 0.4871, 0.4792, 0.4724, 0.4691, 0.4589, 0.4488, 0.4443, 0.4398, 0.4297, 0.4184, 0.4083, 0.4038, 0.396, 0.3847, 0.3757, 0.369, 0.3622, 0.3577, 0.3476, 0.3386, 0.3307, 0.3228, 0.315, 0.3082, 0.3071, 0.3026, 0.2981, 0.2925, 0.288, 0.2801, 0.2756, 0.27, 0.2655, 0.2587, 0.2508, 0.2463, 0.2396, 0.2317, 0.225, 0.2238, 0.2182, 0.2092, 0.2013, 0.1969, 0.1946, 0.1924, 0.1879, 0.1834, 0.1777, 0.1721, 0.1687, 0.1665, 0.1631, 0.1586, 0.1541, 0.1474, 0.1406, 0.1339, 0.1305, 0.1294, 0.1282, 0.1249, 0.1226, 0.1215, 0.1181, 0.1136, 0.1114, 0.1069, 0.1035, 0.099, 0.0956, 0.0945, 0.0934, 0.0922, 0.0922, 0.0911, 0.0889, 0.0877, 0.0877, 0.0855, 0.0821, 0.0776, 0.0697, 0.0686, 0.0686, 0.0664, 0.0664, 0.0664, 0.0652, 0.0619, 0.0585, 0.0574, 0.0574, 0.054, 0.0529, 0.0506, 0.0484, 0.0484, 0.0461, 0.045, 0.0427, 0.0405], "PassYds": [0.9892, 0.9892, 0.986, 0.9849, 0.9849, 0.9795, 0.9752, 0.9699, 0.9677, 0.9666, 0.9656, 0.9645, 0.9602, 0.958, 0.9548, 0.9505, 0.9419, 0.9397, 0.9376, 0.9343, 0.9247, 0.9139, 0.9107, 0.9042, 0.8934, 0.8848, 0.8762, 0.8654, 0.8525, 0.8461, 0.8396, 0.8278, 0.8138, 0.803, 0.7944, 0.7804, 0.7653, 0.7481, 0.7255, 0.7115, 0.6986, 0.6814, 0.6609, 0.6437, 0.6265, 0.605, 0.5823, 0.5587, 0.5404, 0.5296, 0.507, 0.4833, 0.4532, 0.4273, 0.408, 0.3929, 0.3735, 0.3541, 0.3391, 0.3262, 0.3036, 0.2917, 0.2756, 0.2637, 0.2508, 0.2379, 0.2271, 0.2185, 0.2078, 0.1959, 0.1884, 0.1819, 0.1712, 0.1529, 0.1399, 0.1335, 0.1281, 0.1216, 0.1098, 0.1023, 0.0947, 0.0893, 0.0807, 0.0775, 0.071, 0.0667, 0.0614, 0.0581, 0.0571, 0.0571, 0.0549, 0.0527, 0.0474, 0.0474, 0.042, 0.0398, 0.0377, 0.0323, 0.0323, 0.0301, 0.028, 0.028, 0.0248, 0.0215, 0.0205, 0.0161, 0.0151, 0.0151, 0.0151, 0.014, 0.0129, 0.0129, 0.0118, 0.0118, 0.0097, 0.0097, 0.0097, 0.0065, 0.0054, 0.0043, 0.0043, 0.0032, 0.0032, 0.0011, 0.0011, 0.0011, 0.0011, 0.0011, 0.0011, 0.0011, 0.0011, 0.0011, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "Rec": [0.9714, 0.9714, 0.9714, 0.9714, 0.9714, 0.9714, 0.9714, 0.9711, 0.9696, 0.9687, 0.9668, 0.9625, 0.9591, 0.9518, 0.9422, 0.93, 0.9201, 0.9026, 0.8848, 0.8685, 0.8458, 0.8344, 0.8233, 0.8117, 0.8003, 0.7877, 0.7794, 0.7696, 0.7604, 0.7484, 0.737, 0.7253, 0.7088, 0.698, 0.6866, 0.674, 0.6605, 0.6449, 0.628, 0.612, 0.5929, 0.584, 0.568, 0.5536, 0.5404, 0.5293, 0.5152, 0.5035, 0.4937, 0.4817, 0.4673, 0.4568, 0.4458, 0.4332, 0.4224, 0.4111, 0.4003, 0.3939, 0.3834, 0.3724, 0.3598, 0.3527, 0.3422, 0.3346, 0.3269, 0.3207, 0.3121, 0.3014, 0.2897, 0.2836, 0.2756, 0.2691, 0.2602, 0.2541, 0.2467, 0.2366, 0.2326, 0.2237, 0.2154, 0.2083, 0.1982, 0.1911, 0.1849, 0.1794, 0.172, 0.1671, 0.161, 0.1533, 0.1478, 0.1438, 0.1373, 0.1315, 0.1263, 0.1223, 0.1161, 0.1134, 0.1106, 0.106, 0.1011, 0.0974, 0.0931, 0.0906, 0.0876, 0.0857, 0.0811, 0.079, 0.0753, 0.0731, 0.0704, 0.0679, 0.0667, 0.0648, 0.0627, 0.0596, 0.0575, 0.0562, 0.0541, 0.0507, 0.0485, 0.0464, 0.0445, 0.0436, 0.0421, 0.0402, 0.0384, 0.0366, 0.0356, 0.0347, 0.0338, 0.0326, 0.0313, 0.0304, 0.0289, 0.0276, 0.0261, 0.0246, 0.0233, 0.0221, 0.0215, 0.0206, 0.0197, 0.0194, 0.0181, 0.0169, 0.016, 0.0151, 0.0138, 0.0129, 0.0123, 0.012, 0.012], "RecYds": [0.9613, 0.9605, 0.9578, 0.9527, 0.9476, 0.9395, 0.9347, 0.925, 0.9135, 0.9014, 0.8898, 0.8783, 0.8673, 0.8552, 0.8471, 0.8345, 0.8184, 0.8055, 0.7961, 0.7837, 0.7714, 0.7614, 0.7515, 0.738, 0.7273, 0.7155, 0.7061, 0.6961, 0.6857, 0.676, 0.6615, 0.6531, 0.6448, 0.6351, 0.6236, 0.6161, 0.6053, 0.597, 0.5841, 0.572, 0.5613, 0.5505, 0.54, 0.5296, 0.5169, 0.5051, 0.4965, 0.4871, 0.4798, 0.475, 0.4675, 0.4567, 0.4492, 0.4412, 0.4326, 0.4215, 0.4164, 0.406, 0.399, 0.3931, 0.3861, 0.378, 0.3721, 0.3646, 0.3587, 0.3533, 0.3431, 0.3385, 0.3334, 0.3264, 0.3213, 0.3152, 0.3082, 0.302, 0.2966, 0.2896, 0.2832, 0.2783, 0.2724, 0.2657, 0.2614, 0.2558, 0.2488, 0.2421, 0.2372, 0.2329, 0.2286, 0.2233, 0.2192, 0.2136, 0.2085, 0.2023, 0.1991, 0.1951, 0.191, 0.187, 0.1846, 0.1805, 0.176, 0.1711, 0.1685, 0.1663, 0.1631, 0.1599, 0.1561, 0.1539, 0.1513, 0.148, 0.1448, 0.1411, 0.1381, 0.1349, 0.1319, 0.1282, 0.1252, 0.1204, 0.1174, 0.1139, 0.1118, 0.1093, 0.1075, 0.1024, 0.101, 0.0994, 0.0981, 0.0962, 0.094, 0.0913, 0.0895, 0.0884, 0.0873, 0.086, 0.083, 0.0817, 0.0793, 0.0774, 0.0755, 0.0739, 0.0723, 0.0707, 0.0693, 0.0685, 0.0666, 0.0648, 0.0634, 0.0615, 0.0591, 0.057, 0.0551, 0.0543, 0.0529], "RushAtt": [0.9965, 0.9965, 0.9965, 0.9961, 0.9948, 0.9904, 0.9861, 0.973, 0.9678, 0.9656, 0.963, 0.959, 0.9547, 0.9495, 0.9442, 0.9355, 0.9298, 0.922, 0.915, 0.9068, 0.8989, 0.8902, 0.8806, 0.8702, 0.8614, 0.8492, 0.8344, 0.8196, 0.8109, 0.7996, 0.7874, 0.7756, 0.763, 0.7495, 0.7329, 0.7176, 0.6989, 0.6876, 0.6784, 0.6627, 0.6431, 0.6296, 0.6144, 0.5965, 0.5826, 0.5686, 0.5529, 0.5377, 0.5229, 0.5102, 0.4937, 0.4784, 0.4623, 0.4462, 0.434, 0.4161, 0.3991, 0.3852, 0.3725, 0.356, 0.342, 0.3294, 0.3172, 0.3037, 0.2915, 0.278, 0.2667, 0.2553, 0.2449, 0.2366, 0.2248, 0.217, 0.2096, 0.1987, 0.1891, 0.18, 0.1717, 0.1656, 0.1551, 0.1512, 0.1434, 0.139, 0.1316, 0.1259, 0.119, 0.1107, 0.1068, 0.1028, 0.0989, 0.095, 0.0906, 0.0867, 0.0837, 0.0784, 0.0763, 0.0702, 0.0671, 0.0645, 0.0601, 0.0588, 0.0553, 0.0514, 0.0488, 0.0466, 0.0449, 0.0423, 0.0388, 0.0366, 0.0349, 0.0336, 0.0331, 0.0309, 0.0288, 0.0283, 0.0261, 0.0244, 0.0222, 0.0218, 0.0209, 0.0196, 0.0174, 0.0174, 0.0148, 0.0135, 0.0122, 0.0109, 0.0092, 0.0092, 0.0092, 0.0092, 0.0083, 0.0083, 0.0078, 0.007, 0.007, 0.0065, 0.0065, 0.0061, 0.0052, 0.0048, 0.0048, 0.0048, 0.0048, 0.0039, 0.0031, 0.0031, 0.0031, 0.0031, 0.0031, 0.0031, 0.0031], "RushRecYds": [0.9824, 0.981, 0.9771, 0.9689, 0.964, 0.9541, 0.9478, 0.9389, 0.9298, 0.9188, 0.9087, 0.8986, 0.8886, 0.8778, 0.8675, 0.8546, 0.8436, 0.8317, 0.8235, 0.812, 0.8013, 0.7905, 0.7795, 0.7685, 0.7575, 0.747, 0.735, 0.7233, 0.7102, 0.7006, 0.6915, 0.6788, 0.6674, 0.6554, 0.644, 0.633, 0.6227, 0.6126, 0.6014, 0.592, 0.5794, 0.5695, 0.5564, 0.5454, 0.5363, 0.5234, 0.5124, 0.503, 0.4909, 0.482, 0.474, 0.4654, 0.4541, 0.4452, 0.437, 0.4274, 0.4178, 0.4071, 0.3986, 0.3879, 0.3785, 0.3701, 0.3612, 0.3514, 0.3439, 0.3361, 0.3284, 0.3205, 0.3118, 0.3038, 0.2966, 0.2907, 0.2832, 0.2755, 0.2669, 0.2584, 0.25, 0.2439, 0.2336, 0.2264, 0.221, 0.2135, 0.2074, 0.2015, 0.1973, 0.1917, 0.1875, 0.1835, 0.1784, 0.1753, 0.1704, 0.165, 0.1618, 0.158, 0.1543, 0.1489, 0.1458, 0.1426, 0.1381, 0.1344, 0.1311, 0.1269, 0.1234, 0.1199, 0.1168, 0.1117, 0.1081, 0.1053, 0.1032, 0.1004, 0.0976, 0.0946, 0.0913, 0.0887, 0.0861, 0.0845, 0.0803, 0.0789, 0.0763, 0.0749, 0.0719, 0.0698, 0.0681, 0.066, 0.0644, 0.0613, 0.0595, 0.0574, 0.0548, 0.0529, 0.0508, 0.0494, 0.0492, 0.0478, 0.0466, 0.0461, 0.0449, 0.0445, 0.0435, 0.0419, 0.041, 0.04, 0.0396, 0.0377, 0.0363, 0.0358, 0.0346, 0.0332, 0.0325, 0.0318, 0.0309], "RushYds": [0.9606, 0.9585, 0.9483, 0.9436, 0.933, 0.925, 0.9131, 0.9072, 0.897, 0.8894, 0.8766, 0.8682, 0.8601, 0.847, 0.8359, 0.8266, 0.8143, 0.8037, 0.7919, 0.7813, 0.7715, 0.7626, 0.7537, 0.7427, 0.7334, 0.7223, 0.713, 0.6986, 0.6867, 0.6766, 0.6664, 0.6579, 0.6465, 0.6376, 0.6265, 0.6164, 0.6053, 0.5947, 0.585, 0.5727, 0.5617, 0.549, 0.5388, 0.5316, 0.5214, 0.5129, 0.5015, 0.493, 0.4828, 0.4727, 0.4612, 0.4502, 0.4434, 0.4349, 0.4265, 0.4142, 0.4053, 0.3968, 0.3849, 0.3735, 0.3667, 0.3582, 0.3489, 0.3408, 0.3366, 0.3315, 0.3251, 0.3184, 0.3133, 0.3052, 0.2963, 0.2891, 0.2827, 0.2781, 0.2734, 0.2654, 0.2582, 0.2501, 0.2425, 0.2374, 0.2306, 0.2238, 0.22, 0.2149, 0.212, 0.2073, 0.2014, 0.1997, 0.1942, 0.1903, 0.1886, 0.1857, 0.1793, 0.1738, 0.1687, 0.1641, 0.1607, 0.1564, 0.153, 0.1505, 0.1475, 0.1424, 0.1403, 0.1369, 0.1344, 0.1306, 0.1276, 0.1255, 0.1217, 0.1191, 0.1162, 0.1145, 0.1111, 0.1081, 0.1068, 0.1051, 0.103, 0.1017, 0.0996, 0.0967, 0.0937, 0.0903, 0.0882, 0.0869, 0.0848, 0.0831, 0.0814, 0.0801, 0.078, 0.0772, 0.0759, 0.0742, 0.0716, 0.0699, 0.0678, 0.067, 0.0661, 0.064, 0.0627, 0.0623, 0.0602, 0.0572, 0.056, 0.0534, 0.053, 0.0521, 0.0509, 0.0487, 0.0479, 0.0462, 0.0454]}, "PPARAMS": {"PassAtt": {"k": 0, "a": 0, "b": 0}, "PassCmp": {"k": 0, "a": 0.25, "b": 0}, "PassRushYds": {"k": 0, "a": 0.25, "b": 0.25}, "PassTD": {"k": 2, "a": 0.25, "b": 0.75}, "PassYds": {"k": 0, "a": 0.25, "b": 0.25}, "Rec": {"k": 2, "a": 0, "b": 0}, "RecYds": {"k": 3, "a": 0, "b": 0.5}, "RushAtt": {"k": 0, "a": 0, "b": 0.25}, "RushRecYds": {"k": 2, "a": 0.25, "b": 0.5}, "RushYds": {"k": 1, "a": 0.5, "b": 0.5}}, "KEYN": {"0": 0.0, "1": 0.033, "2": 0.0324, "3": 0.1064, "4": 0.0354, "5": 0.0231, "6": 0.0335, "7": 0.0874, "8": 0.0295, "9": 0.0137, "10": 0.0472, "11": 0.0214, "12": 0.0172, "13": 0.0188, "14": 0.0416, "15": 0.0177, "16": 0.0113, "17": 0.041, "18": 0.0223, "19": 0.0155, "20": 0.0177, "21": 0.0367, "22": 0.0147, "23": 0.0118, "24": 0.0282, "25": 0.0169, "26": 0.0105, "27": 0.0169, "28": 0.0265, "29": 0.0094, "30": 0.0054, "31": 0.019, "32": 0.0147, "33": 0.0072, "34": 0.0134, "35": 0.0158}, "KEYN_N": 3730}''')
import os,sys,argparse,datetime,collections,urllib.request,urllib.parse,statistics as st,time
import numpy as np
from openpyxl import Workbook,load_workbook
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.utils import get_column_letter as CL
from openpyxl.formatting.rule import FormulaRule
from openpyxl.worksheet.datavalidation import DataValidation
CFBD='https://api.collegefootballdata.com'
STATS=['PassYds','PassAtt','PassCmp','PassTD','RushYds','RushAtt','RecYds','Rec','RushRecYds','PassRushYds']
THRESH={'PassYds':120,'PassAtt':15,'PassCmp':9,'PassTD':0.7,'RushYds':30,'RushAtt':7,'RecYds':25,'Rec':2.5,'RushRecYds':40,'PassRushYds':140}
CALLS=[0]
def cfbd(path,**q):
    url=f"{CFBD}/{path}?"+urllib.parse.urlencode(q)
    req=urllib.request.Request(url,headers={'Authorization':'Bearer '+os.environ['CFBD_API_KEY']})
    for i in range(3):
        try:
            CALLS[0]+=1;return json.load(urllib.request.urlopen(req,timeout=60))
        except Exception as e:
            err=e;time.sleep(2)
    raise err
def getj(url):
    for i in range(3):
        try: return json.load(urllib.request.urlopen(url,timeout=60))
        except Exception as e: err=e;time.sleep(2)
    return None
# ------------------------------------------------------------------ data
def load(season,week):
    D={}
    D['games']={s:cfbd('games',year=s,seasonType='regular') for s in (season-1,season)}
    D['adv']={s:cfbd('stats/game/advanced',year=s,excludeGarbageTime='true') for s in (season-1,season)}
    D['lines']=cfbd('lines',year=season,seasonType='regular')
    D['ret']=cfbd('player/returning',year=season);D['tal']=cfbd('talent',year=season)
    D['sp']=cfbd('ratings/sp',year=season);D['venues']=cfbd('venues')
    D['plogs']={}
    for s,wks in ((season-1,range(1,16)),(season,range(1,week))):
        for w in wks: D['plogs'][(s,w)]=cfbd('games/players',year=s,week=w,seasonType='regular')
    D['fpi']=getj(f'https://site.web.api.espn.com/apis/fitt/v3/sports/football/college-football/powerindex?season={season}&limit=300')
    D['espn']=getj(f'https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?dates={season}&week={week}&seasontype=2&groups=80&limit=300')
    return D
# ------------------------------------------------------------------ team model
def team_model(D,season,week):
    CO,CD,A,C=CONSTS['CO'],CONSTS['CD'],CONSTS['A'],CONSTS['C']
    G={g['id']:g for s in D['games'] for g in D['games'][s] if g['homeClassification']=='fbs' or g['awayClassification']=='fbs'}
    FBS={s:{t for g in D['games'][s] for t,c in ((g['homeTeam'],g['homeClassification']),(g['awayTeam'],g['awayClassification'])) if c=='fbs'} for s in D['games']}
    OBS=[]
    for s in D['adv']:
        for x in D['adv'][s]:
            o=x['offense']
            if x['gameId'] in G and o.get('ppa') is not None and o.get('plays'):
                OBS.append(dict(gid=x['gameId'],season=s,week=x['week'],team=x['team'],opp=x['opponent'],ppa=o['ppa'],plays=o['plays']))
    tn=lambda t,s:t if t in FBS[s] else 'FCS'
    def hi(o):
        g=G[o['gid']]
        return 0 if g['neutralSite'] else (1 if o['team']==g['homeTeam'] else -1)
    def fit(s,before,prior,lam):
        rows=[o for o in OBS if o['season']==s and o['week']<before]
        teams=sorted({tn(o['team'],s) for o in rows}|{tn(o['opp'],s) for o in rows}|set(prior))
        ix={t:i for i,t in enumerate(teams)};n=len(teams)
        X=np.zeros((len(rows),2*n+2));y=np.zeros(len(rows))
        for r,o in enumerate(rows):
            i,j=tn(o['team'],s),tn(o['opp'],s)
            X[r,ix[i]]=1;X[r,n+ix[j]]=1;X[r,2*n]=1;X[r,2*n+1]=hi(o)
            y[r]=o['ppa']-prior.get(i,(0,0))[0]-prior.get(j,(0,0))[1]
        P=lam*np.eye(2*n+2);P[2*n,2*n]=1e-6;P[2*n+1,2*n+1]=1e-6
        b=np.linalg.solve(X.T@X+P,X.T@y) if len(rows) else np.zeros(2*n+2)
        return {t:(prior.get(t,(0,0))[0]+b[ix[t]],prior.get(t,(0,0))[1]+b[n+ix[t]]) for t in teams}
    END=fit(season-1,99,{},3)
    RET={r['team']:r['percentPPA'] for r in D['ret']};TAL={r['team']:r['talent'] for r in D['tal']}
    tv=np.array([TAL.get(t,np.nan) for t in FBS[season]],dtype=float);m,sd=np.nanmean(tv),np.nanstd(tv)
    P={}
    for t in FBS[season]:
        po,pd=END.get(t,END.get('FCS',(-0.15,0.15)));z=(TAL.get(t,m)-m)/sd;r=RET.get(t,0.5)
        P[t]=(float(np.dot(CO,[po,po*r,z,1])),float(np.dot(CD,[pd,z,1])))
    P['FCS']=END.get('FCS',(-0.2,0.2))
    R=fit(season,week,P,4)
    pl=collections.defaultdict(list)
    for o in OBS:
        if o['season']==season and o['week']<week: pl[o['team']].append(o['plays'])
        if o['season']==season-1: pl[('p',o['team'])].append(o['plays'])
    PACE={t:(sum(pl.get(t,[]))+(np.mean(pl[('p',t)]) if pl.get(('p',t)) else 68.0)*3)/(len(pl.get(t,[]))+3) for t in FBS[season]};PACE['FCS']=64.0
    out=[]
    for g in D['games'][season]:
        if g['week']!=week or (g['homeClassification']!='fbs' and g['awayClassification']!='fbs'): continue
        ht,at=tn(g['homeTeam'],season),tn(g['awayTeam'],season)
        oh,dh=R.get(ht,P.get(ht,(0,0)));oa,da=R.get(at,P.get(at,(0,0)))
        eh,ea=oh+da,oa+dh;pc=PACE.get(ht,64)+PACE.get(at,64)
        out.append(dict(g=g,fcs='FCS' in (ht,at),pm=A[0]*(eh-ea)+A[1]*(0 if g['neutralSite'] else 1),pt=C[0]*(eh+ea)+C[1]*pc+C[2]*(eh+ea)*pc+C[3]))
    ratings=[dict(team=t,off=R[t][0],deff=R[t][1],pace=PACE.get(t),pri_o=P[t][0],pri_d=P[t][1],ret=RET.get(t),tal=TAL.get(t)) for t in FBS[season] if t in R]
    return out,ratings,G
# ------------------------------------------------------------------ player logs
def parse_logs(raw):
    rows={}
    for (season,week),games in raw.items():
        for g in games:
            tm=g['teams']
            for i,t in enumerate(tm):
                opp=tm[1-i]['team'] if len(tm)==2 else None
                for c in t['categories']:
                    for ty in c['types']:
                        for a in ty['athletes']:
                            r=rows.setdefault((g['id'],a['id']),dict(gid=g['id'],season=season,week=week,pid=a['id'],name=a['name'],team=t['team'],opp=opp))
                            v=a['stat'];cn,tnm=c['name'],ty['name']
                            try:
                                if cn=='passing' and tnm=='C/ATT': cm,at=v.split('/');r['PassCmp']=float(cm);r['PassAtt']=float(at)
                                elif cn=='passing' and tnm=='YDS': r['PassYds']=float(v)
                                elif cn=='passing' and tnm=='TD': r['PassTD']=float(v)
                                elif cn=='rushing' and tnm=='CAR': r['RushAtt']=float(v)
                                elif cn=='rushing' and tnm=='YDS': r['RushYds']=float(v)
                                elif cn=='receiving' and tnm=='REC': r['Rec']=float(v)
                                elif cn=='receiving' and tnm=='YDS': r['RecYds']=float(v)
                            except Exception: pass
    out=[]
    for r in rows.values():
        if r['pid'] in ('-1',None): continue
        for k in ['PassCmp','PassAtt','PassYds','PassTD','RushAtt','RushYds','Rec','RecYds']: r.setdefault(k,0.0)
        r['RushRecYds']=r['RushYds']+r['RecYds'];r['PassRushYds']=r['PassYds']+r['RushYds'];out.append(r)
    return out
def player_proj(D,season,week,games_wk):
    L=parse_logs(D['plogs']);cur=[r for r in L if r['season']==season];prv=[r for r in L if r['season']==season-1]
    byp=collections.defaultdict(list);[byp[r['pid']].append(r) for r in cur]
    prior=collections.defaultdict(list);[prior[r['pid']].append(r) for r in prv]
    allowed=collections.defaultdict(lambda:collections.defaultdict(float))
    for r in cur:
        for s in STATS: allowed[(r['opp'],r['gid'])][s]+=r[s]
    acc=collections.defaultdict(lambda:collections.defaultdict(list))
    for (opp,gid),d in allowed.items():
        for s in STATS: acc[opp][s].append(d[s])
    lg={s:np.mean([np.mean(v[s]) for v in acc.values() if v[s]]) for s in STATS}
    tp=collections.defaultdict(list)
    for g in D['games'][season]:
        if g.get('homePoints') is not None and g['week']<week: tp[g['homeTeam']].append(g['homePoints']);tp[g['awayTeam']].append(g['awayPoints'])
    sched={}
    for x in games_wk:
        g=x['g'];sched[g['homeTeam']]=(g,g['awayTeam']);sched[g['awayTeam']]=(g,g['homeTeam'])
    rows=[]
    for pid,h in byp.items():
        team=h[-1]['team']
        if team not in sched: continue
        g,opp=sched[team];name=h[-1]['name']
        pr=prior.get(pid,[])
        for s in STATS:
            PP=CONSTS['PPARAMS'][s];k=PP['k']
            cs=sum(x[s] for x in h);n=len(h);prv_pg=np.mean([x[s] for x in pr]) if len(pr)>=3 else None
            if not prv_pg and n<2: continue
            k=max(k,2) if prv_pg else k
            base=(cs+k*prv_pg)/(n+k) if prv_pg else cs/n
            if base<THRESH[s]*0.8: continue
            if s in('PassYds','PassAtt','PassCmp','PassTD') and np.mean([x['PassAtt'] for x in h])<12: continue
            a=acc.get(opp,{}).get(s,[]);fo=((sum(a)+3*lg[s])/(len(a)+3))/lg[s] if lg[s] else 1
            t=tp.get(team,[]);ts=0.6*(np.mean(t) if t else 28)+0.4*28
            rows.append(dict(name=name,team=team,opp=opp,gid=g['id'],home=team==g['homeTeam'],stat=s,base=base,n=n,prior=prv_pg,fo=fo,a=PP['a'],b=PP['b'],ts=ts))
    return rows,cur
# ------------------------------------------------------------------ weather
def weather(D,games_wk):
    V={v['id']:v for v in D['venues']};out={}
    for x in games_wk:
        g=x['g'];v=V.get(g.get('venueId'))
        if not v or v.get('latitude') is None: continue
        if v.get('dome'): out[g['id']]=('Dome',None,None,None);continue
        ko=datetime.datetime.fromisoformat(g['startDate'].replace('Z','+00:00'))
        days=(ko.date()-datetime.datetime.now(datetime.timezone.utc).date()).days
        if days>15 or days<-1: continue
        j=getj(f"https://api.open-meteo.com/v1/forecast?latitude={v['latitude']}&longitude={v['longitude']}&hourly=temperature_2m,wind_speed_10m,precipitation_probability&wind_speed_unit=mph&temperature_unit=fahrenheit&timezone=UTC&start_date={ko.date()}&end_date={ko.date()}")
        if not j: continue
        hh=ko.strftime('%Y-%m-%dT%H:00')
        try:
            i=j['hourly']['time'].index(hh);hr=j['hourly']
            out[g['id']]=('Outdoor',hr['wind_speed_10m'][i],hr['precipitation_probability'][i],hr['temperature_2m'][i])
        except Exception: pass
    return out
# ------------------------------------------------------------------ workbook
AR='Arial';H=Font(name=AR,bold=True,color='FFFFFF');HF=PatternFill('solid',fgColor='1F3864')
BLUE=Font(name=AR,color='0000FF');BLK=Font(name=AR);GRN=Font(name=AR,color='008000');B=Font(name=AR,bold=True);IT=Font(name=AR,italic=True)
YEL=PatternFill('solid',fgColor='FFFF00');GOOD=PatternFill('solid',fgColor='C6EFCE');LEANF=PatternFill('solid',fgColor='FFF2CC');GREY=PatternFill('solid',fgColor='EDEDED');RED=PatternFill('solid',fgColor='F8CBAD')
FRIENDLY={'PassYds':'Pass Yds','PassAtt':'Pass Att','PassCmp':'Completions','PassTD':'Pass TDs','RushYds':'Rush Yds','RushAtt':'Rush Att','RecYds':'Rec Yds','Rec':'Receptions','RushRecYds':'Rush+Rec Yds','PassRushYds':'Pass+Rush Yds'}
INV={v:k for k,v in FRIENDLY.items()}
# Default Inputs-tab values, exposed for non-Excel (JSON/web) consumers. Keep in sync with the `inp` list in build().
DEFAULT_INPUTS={'hfa':3.0,'w_epa':0.34,'w_sp':0.33,'w_fpi':0.33,'trust_sides':0.85,'trust_totals':0.80,
 'sd_margin':15.25,'sd_total':15.64,'side_strong':5,'side_edge':3.5,'total_bet':4,'total_lean':3,'total_checknews':9,
 'big_spread':24,'wind_thresh':12,'wind_pen':0.3,'prop_play':0.05,'prop_lean':0.025,'top3_budget':100,'bankroll':500,'unit_pct':0.02}
def hdr(ws,row,vals,h=None):
    for i,v in enumerate(vals,1):
        c=ws.cell(row=row,column=i,value=v);c.font=H;c.fill=HF;c.alignment=Alignment(wrap_text=True,vertical='center',horizontal='center')
    if h: ws.row_dimensions[row].height=h
def title(ws,t,sub=None):
    ws['A1']=t;ws['A1'].font=Font(name=AR,bold=True,size=14)
    if sub: ws['A2']=sub;ws['A2'].font=IT
def widths(ws,d):
    for k,v in d.items(): ws.column_dimensions[k].width=v
def et(z):
    d=datetime.datetime.fromisoformat(z.replace('Z','+00:00'))-datetime.timedelta(hours=4);return d.strftime('%a %m/%d %I:%M %p')
def read_prev(path):
    P={'bets':[],'props':[],'entries':[],'inj':[],'pay':[],'inputs':{}}
    if not path or not os.path.exists(path): return P
    wb=load_workbook(path)
    def rows(name,start,ncol,keycol=1):
        if name not in wb.sheetnames: return []
        ws=wb[name];out=[]
        for r in ws.iter_rows(min_row=start,max_col=ncol,values_only=True):
            if r[keycol-1] not in (None,''): out.append(list(r))
        return out
    P['bets']=rows('Bet Log',5,16,4);P['props']=rows('Props Log',5,10,4);P['entries']=rows('Entries',5,6,1)
    P['inj']=rows('Injuries',5,7,1);P['pay']=rows('Payouts',5,3,1)
    if 'Inputs' in wb.sheetnames:
        for r in wb['Inputs'].iter_rows(min_row=4,max_col=2,values_only=True):
            if r[0]: P['inputs'][r[0]]=r[1]
    return P
def build(path,season,week,D,games_wk,ratings,G,proj,cur_logs,wx,prev):
    wb=Workbook()
    lines={l['id']:l for l in D['lines']}
    def book(gid,prov):
        L_=[x for x in lines.get(gid,{}).get('lines',[]) if x.get('spread') is not None]
        for x in L_:
            if x['provider'].replace(' ','').lower()==prov.replace(' ','').lower(): return x
        if prov=='DraftKings':
            for x in L_:
                if x['provider'] not in ('Bovada','teamrankings'): return x
        return None
    espn_ab={};fpi={}
    if D.get('espn'):
        for e in D['espn'].get('events',[]):
            for c in e['competitions'][0]['competitors']: espn_ab[(e['id'],c['homeAway'])]=c['team']['abbreviation']
    if D.get('fpi'):
        for t in D['fpi']['teams']: fpi[int(t['team']['id'])]=t['categories'][0]['values'][0]
    SP={r['team']:r['rating'] for r in D['sp']}
    # ---- Inputs
    wi=wb.active;wi.title='Inputs'
    inp=[('Home field advantage (pts)',3.0,'Applied to SP+ and FPI. EPA model fit gives 2.8.'),
    ('Weight: EPA model',0.34,'Opponent-adjusted EPA/play ratings (CFBD play data, garbage time removed).'),('Weight: SP+',0.33,'SP+ via CFBD.'),('Weight: FPI',0.33,'ESPN FPI.'),
    ('Market trust (sides)',0.85,'Backtest: optimal weight on model vs closing spread ~6%.'),('Market trust (totals)',0.80,'Backtest: optimal weight on model vs closing O/U ~19%.'),
    ('Std dev: margin vs spread',15.25,'CFBD 2022-25.'),('Std dev: total vs O/U',15.64,'CFBD 2022-25.'),
    ('Side "Strong edge" (pts)',5,'All 3 ratings agree. Sides backtest ~51% vs closing lines: bet these early in the week.'),('Side "Edge" (pts)',3.5,'2 of 3 agree.'),
    ('Total BET edge (pts)',4,'Out of sample 2024-25: 4-7 pt edges hit ~56%.'),('Total LEAN edge (pts)',3,''),('Total "check news" edge (pts)',9,'Huge edges usually = market knows something.'),
    ('Big spread cutoff (pts)',24,'Downgrade one tier.'),('Wind threshold (mph)',12,'Assumption, not backtested yet.'),('Total pts removed per mph over threshold',0.3,'Assumption. ~3 pts at 22 mph.'),
    ('Prop PLAY edge (prob over break-even)',0.05,'Pick must beat its break-even by this much.'),('Prop LEAN edge',0.025,''),
    ('Weekly Top 3 budget ($)',100,'Split evenly across the 3 strongest plays (Best Bets, top section).'),('Bankroll ($)',500,'Yours.'),('Unit size (% bankroll)',0.02,'BET = 1 unit, LEAN = 0.5.')]
    title(wi,f'Inputs  |  {season} Week {week}  (blue/yellow = edit; your edits carry forward each week)')
    hdr(wi,3,['Input','Value','Why / Source']);I={}
    for i,(k,v,n) in enumerate(inp,4):
        v=prev['inputs'].get(k,v)
        wi.cell(row=i,column=1,value=k);c=wi.cell(row=i,column=2,value=v);c.font=BLUE;c.fill=YEL;wi.cell(row=i,column=3,value=n);I[k]=f'Inputs!$B${i}'
    r=len(inp)+5;wi.cell(row=r,column=1,value='Unit ($)').font=B;wi.cell(row=r,column=2,value=f"={I['Bankroll ($)']}*{I['Unit size (% bankroll)']}").number_format='$#,##0.00';UNIT=f'Inputs!$B${r}'
    wi.cell(row=r+2,column=1,value=f'Built {datetime.datetime.now().strftime("%m/%d/%Y %H:%M")} UTC from CFBD + ESPN + Open-Meteo. Lines move: confirm before betting.').font=IT
    widths(wi,{'A':40,'B':10,'C':90})
    HFA,WE,WS,WF,TRS,TRT,SDM,SDT,SBE,SLE,TBE,TLE,TCN,BIG,WTH,WPEN,PPE,PLE=[I[k[0]] for k in inp[:18]]
    # ---- Injuries
    wj=wb.create_sheet('Injuries');title(wj,'Injury / QB adjustments (feed the Model)','Pts = points the absence costs the team (negative if a player returns). Active=Y applies it. Carries forward weekly: set N when outdated.')
    hdr(wj,4,['Team (exact name as in Model)','Player','Pos','Status','Pts lost','Active (Y/N)','Source / note'])
    inj=prev['inj'] or [['Kansas','Cole Ballard','QB','OUT (shoulder), 9/18',3.0,'N','Was out vs ASU wk 3. Update status weekly.'],['EXAMPLE','Starter QB','QB','OUT',4.0,'N','P4 starter QB: 3-7 pts. G5: 2-5. Star non-QB: 0.5-1.5.']]
    for i,row in enumerate(inj,5):
        for j,v in enumerate(row[:7],1): c=wj.cell(row=i,column=j,value=v);c.font=BLUE if j in(1,5,6) else BLK
    for i in range(5,60):
        for j in (1,5,6): wj.cell(row=i,column=j).fill=YEL
    widths(wj,{'A':26,'B':20,'C':6,'D':22,'E':9,'F':10,'G':70})
    # ---- Model
    wm=wb.create_sheet('Model')
    cols=['Game','Game ID','Kick (ET)','Away','Home','Neutral','FCS in game','Open home spread','DK home spread','Bovada home spread','Best line home','Best line away','Line move (home)',
    'EPA model margin','Away SP+','Home SP+','SP+ margin','Away FPI','Home FPI','FPI margin','Blended margin','Injury adj (home +)','Manual adj (home +)','Model margin','Market home margin','Edge (pts, + = home)','Ratings agreeing (of 3)','Final proj margin','Home cover prob','Spread pick','Pick prob','Landing % on nearest #','Side tier',
    'Venue','Wind (mph)','Rain %','Temp (F)','Open total','DK total','Bovada total','EPA model total','Weather adj','Total edge','Final proj total','Over prob','Total pick','Total prob','Best total for pick','Total tier','Home ML','Away ML','Home no-vig prob','Model home win prob','ML edge (home)']
    hdr(wm,1,cols,48);wm.freeze_panes='F2';cl={n:CL(i) for i,n in enumerate(cols,1)}
    INP={'Open home spread','DK home spread','Bovada home spread','EPA model margin','Away SP+','Home SP+','Away FPI','Home FPI','Manual adj (home +)','Open total','DK total','Bovada total','EPA model total','Home ML','Away ML','Wind (mph)','Rain %','Temp (F)'}
    gl=sorted(games_wk,key=lambda x:x['g']['startDate'])
    sel=[]
    for i,x in enumerate(gl,2):
        g=x['g'];r=i;dk=book(g['id'],'DraftKings');bv=book(g['id'],'Bovada')
        ha=espn_ab.get((str(g['id']),'home')) or g['homeTeam'][:4].upper();aa=espn_ab.get((str(g['id']),'away')) or g['awayTeam'][:4].upper()
        w=wx.get(g['id'])
        vals={'Game':f'{aa}@{ha}','Game ID':g['id'],'Kick (ET)':et(g['startDate']),'Away':g['awayTeam'],'Home':g['homeTeam'],'Neutral':'Y' if g['neutralSite'] else 'N',
          'FCS in game':'Y' if x['fcs'] else 'N','Open home spread':dk and dk.get('spreadOpen'),'DK home spread':dk and dk.get('spread'),'Bovada home spread':bv and bv.get('spread'),
          'EPA model margin':round(x['pm'],2),'Away SP+':SP.get(g['awayTeam']),'Home SP+':SP.get(g['homeTeam']),'Away FPI':fpi.get(g['awayId']),'Home FPI':fpi.get(g['homeId']),'Manual adj (home +)':0,
          'Venue':(w[0] if w else 'n/a'),'Wind (mph)':(w[1] if w else None),'Rain %':(w[2] if w else None),'Temp (F)':(w[3] if w else None),
          'Open total':dk and dk.get('overUnderOpen'),'DK total':dk and dk.get('overUnder'),'Bovada total':bv and bv.get('overUnder'),'EPA model total':round(x['pt'],2),'Home ML':dk and dk.get('homeMoneyline'),'Away ML':dk and dk.get('awayMoneyline')}
        for n,v in vals.items():
            c=wm.cell(row=r,column=cols.index(n)+1,value=v);c.font=BLUE if n in INP else BLK
        wm.cell(row=r,column=cols.index('Manual adj (home +)')+1).fill=YEL
        C=lambda n:f'{cl[n]}{r}'
        f={'Best line home':f'=IF({C("Bovada home spread")}="",{C("DK home spread")},MAX({C("DK home spread")},{C("Bovada home spread")}))',
        'Best line away':f'=IF({C("Bovada home spread")}="",-{C("DK home spread")},MAX(-{C("DK home spread")},-{C("Bovada home spread")}))',
        'Line move (home)':f'=IF(OR({C("Open home spread")}="",{C("DK home spread")}=""),"",{C("DK home spread")}-{C("Open home spread")})',
        'SP+ margin':f'=IF(OR({C("Away SP+")}="",{C("Home SP+")}=""),"",{C("Home SP+")}-{C("Away SP+")}+IF({C("Neutral")}="Y",0,{HFA}))',
        'FPI margin':f'=IF(OR({C("Away FPI")}="",{C("Home FPI")}=""),"",{C("Home FPI")}-{C("Away FPI")}+IF({C("Neutral")}="Y",0,{HFA}))',
        'Blended margin':f'=IF(OR({C("SP+ margin")}="",{C("FPI margin")}=""),{C("EPA model margin")},{WE}*{C("EPA model margin")}+{WS}*{C("SP+ margin")}+{WF}*{C("FPI margin")})',
        'Injury adj (home +)':f'=SUMIFS(Injuries!$E:$E,Injuries!$A:$A,{C("Away")},Injuries!$F:$F,"Y")-SUMIFS(Injuries!$E:$E,Injuries!$A:$A,{C("Home")},Injuries!$F:$F,"Y")',
        'Model margin':f'={C("Blended margin")}+{C("Injury adj (home +)")}+{C("Manual adj (home +)")}',
        'Market home margin':f'=IF({C("DK home spread")}="","",-{C("DK home spread")})',
        'Edge (pts, + = home)':f'=IF({C("Market home margin")}="","",{C("Model margin")}-{C("Market home margin")})',
        'Ratings agreeing (of 3)':f'=IF(OR({C("Edge (pts, + = home)")}="",{C("SP+ margin")}="",{C("FPI margin")}=""),"",(SIGN({C("EPA model margin")}-{C("Market home margin")})=SIGN({C("Edge (pts, + = home)")}))+(SIGN({C("SP+ margin")}-{C("Market home margin")})=SIGN({C("Edge (pts, + = home)")}))+(SIGN({C("FPI margin")}-{C("Market home margin")})=SIGN({C("Edge (pts, + = home)")})))',
        'Final proj margin':f'=IF({C("Market home margin")}="","",{TRS}*{C("Market home margin")}+(1-{TRS})*{C("Model margin")})',
        'Home cover prob':f'=IF({C("Final proj margin")}="","",NORMSDIST(({C("Final proj margin")}+{C("DK home spread")})/{SDM}))',
        'Spread pick':f'=IF({C("Home cover prob")}="","",IF({C("Home cover prob")}>=0.5,{C("Home")}&" "&TEXT({C("Best line home")},"+0.0;-0.0;PK"),{C("Away")}&" "&TEXT({C("Best line away")},"+0.0;-0.0;PK")))',
        'Pick prob':f'=IF({C("Home cover prob")}="","",MAX({C("Home cover prob")},1-{C("Home cover prob")}))',
        'Landing % on nearest #':f'=IF({C("DK home spread")}="","",IFERROR(INDEX(\'Key Numbers\'!$B$4:$B$39,MATCH(MIN(35,ROUND(ABS({C("DK home spread")}),0)),\'Key Numbers\'!$A$4:$A$39,0)),""))',
        'Side tier':f'=IF({C("Edge (pts, + = home)")}="","",IF({C("FCS in game")}="Y","No bet: FCS",IF(AND(ABS({C("Edge (pts, + = home)")})>={SBE},{C("Ratings agreeing (of 3)")}=3),IF(ABS({C("DK home spread")})>={BIG},"Edge","Strong edge"),IF(AND(ABS({C("Edge (pts, + = home)")})>={SLE},{C("Ratings agreeing (of 3)")}>=2),IF(ABS({C("DK home spread")})>={BIG},"Pass","Edge"),"Pass"))))',
        'Weather adj':f'=IF({C("Wind (mph)")}="",0,-MAX(0,{C("Wind (mph)")}-{WTH})*{WPEN})',
        'Total edge':f'=IF({C("DK total")}="","",{C("EPA model total")}+{C("Weather adj")}-{C("DK total")})',
        'Final proj total':f'=IF({C("DK total")}="","",{TRT}*{C("DK total")}+(1-{TRT})*({C("EPA model total")}+{C("Weather adj")}))',
        'Over prob':f'=IF({C("Final proj total")}="","",1-NORMSDIST(({C("DK total")}-{C("Final proj total")})/{SDT}))',
        'Total pick':f'=IF({C("Over prob")}="","",IF({C("Over prob")}>=0.5,"Over "&{C("DK total")},"Under "&{C("DK total")}))',
        'Total prob':f'=IF({C("Over prob")}="","",MAX({C("Over prob")},1-{C("Over prob")}))',
        'Best total for pick':f'=IF({C("Over prob")}="","",IF({C("Over prob")}>=0.5,IF({C("Bovada total")}="",{C("DK total")},MIN({C("DK total")},{C("Bovada total")})),IF({C("Bovada total")}="",{C("DK total")},MAX({C("DK total")},{C("Bovada total")}))))',
        'Total tier':f'=IF({C("Total edge")}="","",IF({C("FCS in game")}="Y","No bet: FCS",IF(ABS({C("Total edge")})>={TCN},IF(AND({C("Open total")}<>"",SIGN({C("DK total")}-{C("Open total")})=SIGN({C("Total edge")})),"BET","Check news"),IF(ABS({C("Total edge")})>={TBE},IF(ABS({C("DK home spread")})>={BIG},"LEAN","BET"),IF(ABS({C("Total edge")})>={TLE},"LEAN","Pass")))))',
        'Home no-vig prob':f'=IF(OR({C("Home ML")}="",{C("Away ML")}=""),"",IF({C("Home ML")}<0,-{C("Home ML")}/(-{C("Home ML")}+100),100/({C("Home ML")}+100))/(IF({C("Home ML")}<0,-{C("Home ML")}/(-{C("Home ML")}+100),100/({C("Home ML")}+100))+IF({C("Away ML")}<0,-{C("Away ML")}/(-{C("Away ML")}+100),100/({C("Away ML")}+100))))',
        'Model home win prob':f'=IF({C("Final proj margin")}="","",NORMSDIST({C("Final proj margin")}/{SDM}))',
        'ML edge (home)':f'=IF(OR({C("Home no-vig prob")}="",{C("Model home win prob")}=""),"",{C("Model home win prob")}-{C("Home no-vig prob")})'}
        for n,v in f.items(): wm.cell(row=r,column=cols.index(n)+1,value=v)
        for n in ('Home cover prob','Pick prob','Landing % on nearest #','Over prob','Total prob','Home no-vig prob','Model home win prob','ML edge (home)'): wm[C(n)].number_format='0.0%'
        for n in ('EPA model margin','SP+ margin','FPI margin','Blended margin','Model margin','Edge (pts, + = home)','Final proj margin','EPA model total','Weather adj','Total edge','Final proj total'): wm[C(n)].number_format='0.0;-0.0;0.0'
        # python mirror for Best Bets selection (default inputs)
        if dk and dk.get('spread') is not None and dk.get('overUnder') is not None and not x['fcs']:
            wind=w[1] if w and w[1] is not None else 0
            te=x['pt']-max(0,wind-12)*0.3-dk['overUnder'];mv=(dk['overUnder']-dk['overUnderOpen']) if dk.get('overUnderOpen') else 0
            comps=[x['pm']];h=0 if g['neutralSite'] else 3.0
            if SP.get(g['homeTeam']) is not None and SP.get(g['awayTeam']) is not None: comps.append(SP[g['homeTeam']]-SP[g['awayTeam']]+h)
            if fpi.get(g['homeId']) is not None and fpi.get(g['awayId']) is not None: comps.append(fpi[g['homeId']]-fpi[g['awayId']]+h)
            mk=-dk['spread'];bl=(0.34*comps[0]+0.33*comps[1]+0.33*comps[2]) if len(comps)==3 else comps[0];se=bl-mk
            agree=sum(np.sign(c-mk)==np.sign(se) for c in comps) if len(comps)==3 else 0
            sel.append(dict(key=f'{aa}@{ha}',gid=g['id'],kick=g['startDate'],te=te,mv=mv,ou=dk['overUnder'],sp=dk['spread'],se=se,agree=agree,home=g['homeTeam'],away=g['awayTeam'],wind=wind))
    last=len(gl)+1
    for c in range(1,len(cols)+1): wm.column_dimensions[CL(c)].width=10
    for n,wd in [('Game',12),('Kick (ET)',16),('Away',18),('Home',18),('Spread pick',24),('Side tier',13),('Total pick',12),('Total tier',13),('Venue',9)]: wm.column_dimensions[cl[n]].width=wd
    st_,tt=cl['Side tier'],cl['Total tier']
    wm.conditional_formatting.add(f'A2:{st_}{last}',FormulaRule(formula=[f'${st_}2="Strong edge"'],fill=GOOD))
    wm.conditional_formatting.add(f'A2:{st_}{last}',FormulaRule(formula=[f'${st_}2="Edge"'],fill=LEANF))
    rg=f'{cl["Venue"]}2:{tt}{last}'
    wm.conditional_formatting.add(rg,FormulaRule(formula=[f'${tt}2="BET"'],fill=GOOD));wm.conditional_formatting.add(rg,FormulaRule(formula=[f'${tt}2="LEAN"'],fill=LEANF));wm.conditional_formatting.add(rg,FormulaRule(formula=[f'${tt}2="Check news"'],fill=RED))
    wm.auto_filter.ref=f'A1:{CL(len(cols))}{last}'
    wm.cell(row=last+2,column=1,value='DK columns fall back to another book (e.g., ESPN Bet) when DraftKings has not posted yet. Sources: CFBD (EPA, SP+, DraftKings/Bovada lines), ESPN (FPI), Open-Meteo (forecast at kickoff). EPA margin/total are engine outputs; everything else recalculates.').font=IT
    MR=lambda n:f"Model!${cl[n]}:${cl[n]}"
    # ---- Best Bets
    wbb=wb.create_sheet('Best Bets',0)
    title(wbb,f'Best Bets  |  {season} Week {week}',f'Built {datetime.datetime.now().strftime("%a %m/%d")}. Early-week build = bet sides now; totals can wait for Saturday refresh. Props: enter lines on Props Board.')
    hdr(wbb,4,['Tier','Game','Kick (ET)','Bet','Type','Model edge (pts)','Model tier (live)','Stake ($)','Note','Bet only if line is','Model number'],32)
    picks=[]
    for s in sel:
        a=abs(s['te'])
        if a>=9 and np.sign(s['mv'])==np.sign(s['te']) and s['mv']!=0: picks.append(('2',s,'Total',f"{'Over' if s['te']>0 else 'Under'} {s['ou']}",'7+ pt edge, line already moving our way. Half stake.'))
        elif a>=9: picks.append(('Pass',s,'Total',f"{'Over' if s['te']>0 else 'Under'} {s['ou']}",'Edge too big: check news (injury/weather) first.'))
        elif a>=4: picks.append(('1' if abs(s['sp'])<24 else '2',s,'Total',f"{'Over' if s['te']>0 else 'Under'} {s['ou']}",'Totals edge in the backtested 4-7+ pt range.' + (' Wind %s mph.'%round(s['wind']) if s['wind']>=12 else '')))
    for s in sel:
        if abs(s['se'])>=5 and s['agree']==3 and abs(s['sp'])<24:
            side=s['home'] if s['se']>0 else s['away'];line=s['sp'] if s['se']>0 else -s['sp']
            picks.append(('Side',s,'Spread',f"{side} {line:+g}",'All 3 ratings agree. Side edges beat OPENING lines in backtest (~53%, +CLV), not closing. Bet early or pass.'))
    order={'1':0,'2':1,'Side':2,'Pass':3};picks.sort(key=lambda p:(order[p[0]],p[1]['kick']))
    for i,(tier,s,typ,bet,note) in enumerate(picks,5):
        r=i;M=lambda n:f'INDEX({MR(n)},MATCH($B{r},{MR("Game")},0))'
        wbb.cell(row=r,column=1,value=tier).font=B;wbb.cell(row=r,column=2,value=s['key']).font=BLUE;wbb.cell(row=r,column=3,value='='+M('Kick (ET)')).font=GRN
        wbb.cell(row=r,column=4,value=bet).font=B;wbb.cell(row=r,column=5,value=typ)
        wbb.cell(row=r,column=6,value='='+M('Total edge' if typ=='Total' else 'Edge (pts, + = home)')).font=GRN;wbb.cell(row=r,column=6).number_format='+0.0;-0.0;0.0'
        wbb.cell(row=r,column=7,value='='+M('Total tier' if typ=='Total' else 'Side tier')).font=GRN
        wbb.cell(row=r,column=8,value=f'=IF(A{r}="1",{UNIT},IF(OR(A{r}="2",A{r}="Side"),{UNIT}*0.5,0))').number_format='$#,##0.00'
        wbb.cell(row=r,column=9,value=note)
        if typ=='Total':
            mt='('+M('EPA model total')+'+'+M('Weather adj')+')'
            wbb.cell(row=r,column=11,value='='+mt).number_format='0.0'
            wbb.cell(row=r,column=10,value=f'=IF(LEFT(D{r},4)="Over","at or below "&TEXT(FLOOR(K{r}-{TBE},0.5),"0.0"),"at or above "&TEXT(CEILING(K{r}+{TBE},0.5),"0.0"))')
        else:
            wbb.cell(row=r,column=11,value='='+M('Model margin')).number_format='+0.0;-0.0'
            home=s['se']>0
            wbb.cell(row=r,column=10,value=(f'="{s["home"]} "&TEXT(CEILING({SBE}-K{r},0.5),"+0.0;-0.0")&" or better"' if home else f'="{s["away"]} "&TEXT(CEILING({SBE}+K{r},0.5),"+0.0;-0.0")&" or better"'))
        wbb.cell(row=r,column=10).font=B
        fill={'1':GOOD,'2':LEANF,'Side':GREY}.get(tier,RED)
        for c in range(1,9): wbb.cell(row=r,column=c).fill=fill
    if not picks: wbb.cell(row=5,column=1,value='No qualifying plays this build.')
    # Top 3 rule: totals with 4 <= |edge| < 7 ranked by edge, then 7+ totals moving our way, then strong sides
    def rank(p):
        t,s,typ,bet,n=p;a=abs(s['te']) if typ=='Total' else abs(s['se'])
        if typ=='Total' and 4<=a<7: return (0,-a)
        if typ=='Total' and t=='2': return (1,-a)
        if typ=='Spread': return (2,-a)
        return (9,0)
    top=[p for p in sorted(picks,key=rank) if rank(p)[0]<9][:3]
    r0=len(picks)+7
    wbb.cell(row=r0,column=1,value='TOP 3: the week\'s strongest plays, budget split evenly').font=Font(name=AR,bold=True,size=12)
    hdr(wbb,r0+1,['#','Game','Kick (ET)','Bet','Type','Model edge (pts)','Stake ($)','','Rule'])
    for j,(t,s,typ,bet,n) in enumerate(top,1):
        rr=r0+1+j
        wbb.cell(row=rr,column=1,value=j);wbb.cell(row=rr,column=2,value=s['key']);wbb.cell(row=rr,column=3,value=et(s['kick']));wbb.cell(row=rr,column=4,value=bet).font=B;wbb.cell(row=rr,column=5,value=typ)
        wbb.cell(row=rr,column=6,value=round(s['te'] if typ=='Total' else s['se'],1))
        wbb.cell(row=rr,column=7,value=f"={I['Weekly Top 3 budget ($)']}/{len(top)}").number_format='$#,##0.00'
        for c in range(1,8): wbb.cell(row=rr,column=c).fill=GOOD
    wbb.cell(row=r0+2,column=9,value='Ranked: totals with a 4-7 pt edge first (best backtest bucket), then bigger totals edges already moving our way, then strong sides. Still check the "Bet only if line is" cutoff above.')
    widths(wbb,{'A':6,'B':13,'C':17,'D':26,'E':8,'F':10,'G':12,'H':10,'I':70,'J':24,'K':10})
    # ---- Projections (players)
    wp=wb.create_sheet('Projections')
    title(wp,f'Player projections  |  Week {week}','Base = per-game average (2026, blended with 2025 prior). Opp factor = what the defense allows vs average. Volume = implied team total vs team average. Updates live if Model lines change.')
    pcol=['Key (Player|Stat)','Player','Team','Opponent','Game ID','Home?','Stat','Games (2026)','2025 per game','Base','Opp factor','Opp exp','Vol exp','Team avg pts (shrunk)','Implied team total','Volume factor','Projection','Dup name?']
    hdr(wp,4,pcol,40)
    proj.sort(key=lambda p:(p['stat'],-p['base']))
    for i,p in enumerate(proj,5):
        r=i;fs=FRIENDLY[p['stat']]
        vals=[f'=B{r}&"|"&G{r}',p['name'],p['team'],p['opp'],p['gid'],'Y' if p['home'] else 'N',fs,p['n'],p['prior'],round(p['base'],2),round(p['fo'],3),p['a'],p['b'],round(p['ts'],2)]
        for j,v in enumerate(vals,1): c=wp.cell(row=r,column=j,value=v);c.font=BLUE if j in (8,9,10,11,12,13,14) else BLK
        dks=f'INDEX({MR("DK home spread")},MATCH(E{r},{MR("Game ID")},0))';dkt=f'INDEX({MR("DK total")},MATCH(E{r},{MR("Game ID")},0))'
        wp.cell(row=r,column=15,value=f'=IFERROR(IF(OR({dkt}="",{dks}=""),N{r},IF(F{r}="Y",{dkt}/2-{dks}/2,{dkt}/2+{dks}/2)),N{r})')
        wp.cell(row=r,column=16,value=f'=MAX(0.3,O{r})/N{r}')
        wp.cell(row=r,column=17,value=f'=J{r}*K{r}^L{r}*P{r}^M{r}')
        wp.cell(row=r,column=18,value=f'=IF(COUNTIF($A$5:$A${len(proj)+4},A{r})>1,"DUP","")')
        for j in (9,10,14,15,17): wp.cell(row=r,column=j).number_format='0.0'
        wp.cell(row=r,column=11).number_format='0.00';wp.cell(row=r,column=16).number_format='0.00'
    PLAST=len(proj)+4
    widths(wp,{'A':30,'B':22,'C':18,'D':18,'G':13});wp.freeze_panes='C5';wp.auto_filter.ref=f'A4:R{PLAST}'
    # ---- Prop Dist
    wd=wb.create_sheet('Prop Dist');title(wd,'P(actual > ratio x projection), 2025 out-of-sample games','Empirical: rushing/receiving are right-skewed, so the median is BELOW the average. That is why "Less" at a line equal to the average wins more than half.')
    hdr(wd,3,['Line / projection']+[FRIENDLY[s] for s in STATS])
    for i,g_ in enumerate(CONSTS['GRID'],4):
        wd.cell(row=i,column=1,value=g_)
        for j,s in enumerate(STATS,2): c=wd.cell(row=i,column=j,value=CONSTS['DIST'][s][i-4]);c.number_format='0.0%'
    DL=3+len(CONSTS['GRID'])
    # ---- Payouts
    wy=wb.create_sheet('Payouts');title(wy,'Pick\'em payouts (EDIT to match your app; carries forward)','Break-even per pick = (1 / payout)^(1 / picks). DraftKings props use the actual odds instead.')
    hdr(wy,4,['App','Picks','Payout (x)','Break-even per pick'])
    pay=prev['pay'] or [[a,n,p] for a in ('Sleeper','Underdog') for n,p in ((2,3),(3,6),(4,10),(5,20),(6,25))]
    for i,(a,n,p) in enumerate(pay,5):
        wy.cell(row=i,column=1,value=a).font=BLUE;wy.cell(row=i,column=2,value=n).font=BLUE;c=wy.cell(row=i,column=3,value=p);c.font=BLUE;c.fill=YEL
        wy.cell(row=i,column=4,value=f'=(1/C{i})^(1/B{i})').number_format='0.0%'
    widths(wy,{'A':12,'B':8,'C':11,'D':18})
    # ---- Props Board
    wpb=wb.create_sheet('Props Board',1)
    title(wpb,f'Props Board  |  Week {week}','Enter: App, Player (exact name from Projections), Stat (dropdown), Line, # picks in entry (Sleeper/Underdog) or DK odds. Paste screenshots to Claude and I will fill it.')
    bcol=['App','Player','Stat','Line','Picks in entry','DK Over odds','DK Under odds','Team','Game ID','Projection','Model P(over)','Model pick','Model prob','DK no-vig prob (pick)','Blended prob','Break-even','Edge','Tier','Same-game picks','Notes']
    hdr(wpb,4,bcol,40)
    lined={x['gid'] for x in sel}
    ex=[p for p in proj if p['stat']=='PassYds' and p['gid'] in lined][:1]
    for r in range(5,205):
        k=f'B{r}&"|"&C{r}'
        f={8:f'=IF(B{r}="","",IFERROR(INDEX(Projections!$C:$C,MATCH({k},Projections!$A:$A,0)),"Not found"))',
           9:f'=IF(B{r}="","",IFERROR(INDEX(Projections!$E:$E,MATCH({k},Projections!$A:$A,0)),""))',
           10:f'=IF(B{r}="","",IFERROR(INDEX(Projections!$Q:$Q,MATCH({k},Projections!$A:$A,0)),""))',
           11:f'=IF(OR(J{r}="",D{r}=""),"",INDEX(\'Prop Dist\'!$B$4:$K${DL},MATCH(MIN(3,D{r}/MAX(0.01,J{r})),\'Prop Dist\'!$A$4:$A${DL},1),MATCH(C{r},\'Prop Dist\'!$B$3:$K$3,0)))',
           12:f'=IF(K{r}="","",IF(K{r}>=0.5,"More","Less"))',
           13:f'=IF(K{r}="","",MAX(K{r},1-K{r}))',
           14:f'=IF(OR(F{r}="",G{r}="",L{r}=""),"",IF(L{r}="More",IF(F{r}<0,-F{r}/(-F{r}+100),100/(F{r}+100)),IF(G{r}<0,-G{r}/(-G{r}+100),100/(G{r}+100)))/(IF(F{r}<0,-F{r}/(-F{r}+100),100/(F{r}+100))+IF(G{r}<0,-G{r}/(-G{r}+100),100/(G{r}+100))))',
           15:f'=IF(M{r}="","",IF(N{r}="",M{r},(M{r}+N{r})/2))',
           16:f'=IF(M{r}="","",IF(A{r}="DraftKings",IF(L{r}="More",IF(F{r}="","",IF(F{r}<0,-F{r}/(-F{r}+100),100/(F{r}+100))),IF(G{r}="","",IF(G{r}<0,-G{r}/(-G{r}+100),100/(G{r}+100)))),IFERROR(INDEX(Payouts!$D:$D,MATCH(1,INDEX((Payouts!$A:$A=A{r})*(Payouts!$B:$B=E{r}),0),0)),"")))',
           17:f'=IF(OR(O{r}="",P{r}=""),"",O{r}-P{r})',
           18:f'=IF(Q{r}="","",IF(Q{r}>={PPE},"PLAY",IF(Q{r}>={PLE},"LEAN","Pass")))',
           19:f'=IF(I{r}="","",COUNTIF($I$5:$I$204,I{r}))'}
        for j,v in f.items(): wpb.cell(row=r,column=j,value=v)
        for j in (11,13,14,15,16,17): wpb.cell(row=r,column=j).number_format='0.0%'
        wpb.cell(row=r,column=10).number_format='0.0'
        for j in range(1,8): wpb.cell(row=r,column=j).fill=YEL;wpb.cell(row=r,column=j).font=BLUE
    if ex:
        e=ex[0];wpb['A5']='Sleeper';wpb['B5']=e['name'];wpb['C5']='Pass Yds';wpb['D5']=round(e['base'])+0.5;wpb['E5']=3;wpb['T5']='EXAMPLE row: delete or overwrite.'
    dv=DataValidation(type='list',formula1='"Sleeper,Underdog,DraftKings"',allow_blank=True);wpb.add_data_validation(dv);dv.add('A5:A204')
    dv2=DataValidation(type='list',formula1='"'+','.join(FRIENDLY[s] for s in STATS)+'"',allow_blank=True);wpb.add_data_validation(dv2);dv2.add('C5:C204')
    wpb.conditional_formatting.add('A5:T204',FormulaRule(formula=['$R5="PLAY"'],fill=GOOD));wpb.conditional_formatting.add('A5:T204',FormulaRule(formula=['$R5="LEAN"'],fill=LEANF))
    wpb.conditional_formatting.add('S5:S204',FormulaRule(formula=['$S5>1'],fill=RED))
    widths(wpb,{'A':11,'B':22,'C':13,'D':7,'E':8,'F':8,'G':8,'H':16,'I':11,'T':30});wpb.freeze_panes='D5'
    # ---- Bet Log (season)
    wl=wb.create_sheet('Bet Log');title(wl,'Season Bet Log: sides & totals (carries forward; engine fills scores + closing lines)','You enter blue columns. Game ID comes from the Model tab. Type: Spread / Over / Under / ML. Side: team name for Spread/ML.')
    lc=['Week','Date','Game ID','Game','Type','Side','Line taken','Odds','Stake ($)','Closing line (auto)','CLV (pts)','Home pts (auto)','Away pts (auto)','Side is home (auto)','Result','Profit ($)']
    hdr(wl,4,lc,40)
    bets=prev['bets']
    gid_scores={g['id']:g for s in D['games'] for g in D['games'][s]}
    for b in bets:
        gid=b[2]
        try: gid=int(gid)
        except Exception: gid=None
        g=gid_scores.get(gid)
        if g:
            if g.get('homePoints') is not None: b[11]=g['homePoints'];b[12]=g['awayPoints']
            side=str(b[5] or '')
            b[13]='Y' if side and (side==g['homeTeam'] or side in g['homeTeam']) else ('N' if side else b[13])
            dk=book(gid,'DraftKings')
            if dk and b[9] in (None,'') and g.get('completed'):
                if b[4] in ('Over','Under'): b[9]=dk.get('overUnder')
                elif b[4]=='Spread' and dk.get('spread') is not None and b[13] in ('Y','N'): b[9]=dk['spread'] if b[13]=='Y' else -dk['spread']
    for i,b in enumerate(bets,5):
        r=i
        for j in range(10):
            if j<len(b): c=wl.cell(row=r,column=j+1,value=b[j]);c.font=BLUE
        for j in (11,12,13):
            if j<len(b) and b[j] not in (None,''): wl.cell(row=r,column=j+1,value=b[j])
    for r in range(5,5+len(bets)+150):
        wl.cell(row=r,column=11,value=f'=IF(OR(J{r}="",G{r}=""),"",IF(E{r}="Over",J{r}-G{r},IF(OR(E{r}="Under",E{r}="Spread"),G{r}-J{r},"")))')
        mg=f'IF(N{r}="Y",L{r}-M{r},M{r}-L{r})'
        wl.cell(row=r,column=15,value=f'=IF(OR(L{r}="",M{r}="",E{r}=""),"",IF(E{r}="Over",IF(L{r}+M{r}>G{r},"W",IF(L{r}+M{r}<G{r},"L","P")),IF(E{r}="Under",IF(L{r}+M{r}<G{r},"W",IF(L{r}+M{r}>G{r},"L","P")),IF(N{r}="","",IF(E{r}="Spread",IF({mg}+G{r}>0,"W",IF({mg}+G{r}<0,"L","P")),IF({mg}>0,"W","L"))))))')
        wl.cell(row=r,column=16,value=f'=IF(O{r}="","",IF(O{r}="W",I{r}*IF(H{r}<0,100/-H{r},H{r}/100),IF(O{r}="L",-I{r},0)))')
        wl.cell(row=r,column=16).number_format='$#,##0.00;($#,##0.00);-';wl.cell(row=r,column=9).number_format='$#,##0.00'
        for j in (1,2,3,4,5,6,7,8,9): wl.cell(row=r,column=j).fill=YEL
    dvt=DataValidation(type='list',formula1='"Spread,Over,Under,ML"',allow_blank=True);wl.add_data_validation(dvt);dvt.add(f'E5:E{len(bets)+155}')
    widths(wl,{'A':6,'B':11,'C':11,'D':12,'E':8,'F':18,'G':9,'H':7,'I':9,'J':10,'K':8,'L':8,'M':8,'N':8,'O':7,'P':10});wl.freeze_panes='A5'
    BLAST=len(bets)+154
    # ---- Props Log + Entries
    wpl=wb.create_sheet('Props Log');title(wpl,'Season Props Log (engine fills Actual after games)','One row per leg. Entry ID ties legs to an entry on the Entries tab.')
    hdr(wpl,4,['Week','App','Entry ID','Player','Stat','Line','Pick (More/Less)','Projection at bet','Actual (auto)','Result'],32)
    props=prev['props'];byname=collections.defaultdict(list)
    for x in cur_logs: byname[(x['name'].lower(),x['week'])].append(x)
    for p in props:
        if p[8] in (None,'') and p[0] and p[3] and p[4] in INV:
            m=byname.get((str(p[3]).lower(),int(p[0])))
            if m: p[8]=m[0][INV[p[4]]]
    for i,p in enumerate(props,5):
        for j in range(9):
            if j<len(p): c=wpl.cell(row=i,column=j+1,value=p[j]);c.font=BLUE if j<8 else BLK
    for r in range(5,5+len(props)+300):
        wpl.cell(row=r,column=10,value=f'=IF(OR(I{r}="",F{r}=""),"",IF(I{r}=F{r},"P",IF((I{r}>F{r})=(G{r}="More"),"W","L")))')
        for j in range(1,9): wpl.cell(row=r,column=j).fill=YEL
    dvp=DataValidation(type='list',formula1='"More,Less"',allow_blank=True);wpl.add_data_validation(dvp);dvp.add(f'G5:G{len(props)+305}')
    widths(wpl,{'A':6,'B':10,'C':9,'D':22,'E':13,'F':7,'G':9,'H':10,'I':9,'J':7});wpl.freeze_panes='A5'
    PL=len(props)+304
    we=wb.create_sheet('Entries');title(we,'Pick\'em entries (profit by entry)','Stake and payout per entry. Pushes: most apps drop the leg and reduce the payout, so check the app and override Profit if needed.')
    hdr(we,4,['Entry ID','App','Week','Stake ($)','Payout (x)','Picks (auto)','Legs graded','Legs won','Legs lost','Result','Profit ($)'],32)
    ents=prev['entries']
    for i,e in enumerate(ents,5):
        for j in range(5):
            if j<len(e): c=we.cell(row=i,column=j+1,value=e[j]);c.font=BLUE
    for r in range(5,5+len(ents)+150):
        we.cell(row=r,column=6,value=f"=IF(A{r}=\"\",\"\",COUNTIF('Props Log'!$C$5:$C${PL},A{r}))")
        we.cell(row=r,column=7,value=f"=IF(A{r}=\"\",\"\",COUNTIFS('Props Log'!$C$5:$C${PL},A{r},'Props Log'!$J$5:$J${PL},\"?*\"))")
        we.cell(row=r,column=8,value=f"=IF(A{r}=\"\",\"\",COUNTIFS('Props Log'!$C$5:$C${PL},A{r},'Props Log'!$J$5:$J${PL},\"W\"))")
        we.cell(row=r,column=9,value=f"=IF(A{r}=\"\",\"\",COUNTIFS('Props Log'!$C$5:$C${PL},A{r},'Props Log'!$J$5:$J${PL},\"L\"))")
        we.cell(row=r,column=10,value=f'=IF(OR(A{r}="",F{r}=0),"",IF(I{r}>0,"L",IF(G{r}<F{r},"Pending",IF(H{r}=F{r},"W","Push-check app"))))')
        we.cell(row=r,column=11,value=f'=IF(J{r}="W",D{r}*(E{r}-1),IF(J{r}="L",-D{r},""))')
        we.cell(row=r,column=11).number_format='$#,##0.00;($#,##0.00);-'
        for j in range(1,6): we.cell(row=r,column=j).fill=YEL
    widths(we,{'A':9,'B':10,'C':6,'D':9,'E':9,'F':8,'G':8,'H':8,'I':8,'J':13,'K':10});EL=len(ents)+154
    # ---- Dashboard
    ws=wb.create_sheet('Season Dashboard',1);title(ws,f'{season} Season Dashboard','All formulas off Bet Log, Props Log, Entries.')
    hdr(ws,4,['Market','Bets','W','L','P','Win %','Profit ($)','Avg CLV (pts)','% beating close'])
    for i,t in enumerate(['Spread','Over','Under','ML','All sides/totals'],5):
        crit='"*"' if t.startswith('All') else f'"{t}"'
        ws.cell(row=i,column=1,value=t).font=B
        ws.cell(row=i,column=2,value=f"=COUNTIFS('Bet Log'!$E$5:$E${BLAST},{crit},'Bet Log'!$O$5:$O${BLAST},\"?*\")")
        for j,res in ((3,'W'),(4,'L'),(5,'P')): ws.cell(row=i,column=j,value=f"=COUNTIFS('Bet Log'!$E$5:$E${BLAST},{crit},'Bet Log'!$O$5:$O${BLAST},\"{res}\")")
        ws.cell(row=i,column=6,value=f'=IFERROR(C{i}/(C{i}+D{i}),"")').number_format='0.0%'
        ws.cell(row=i,column=7,value=f"=SUMIFS('Bet Log'!$P$5:$P${BLAST},'Bet Log'!$E$5:$E${BLAST},{crit})").number_format='$#,##0.00;($#,##0.00);-'
        ws.cell(row=i,column=8,value=f"=IFERROR(AVERAGEIFS('Bet Log'!$K$5:$K${BLAST},'Bet Log'!$E$5:$E${BLAST},{crit}),\"\")").number_format='0.00'
        ws.cell(row=i,column=9,value=f"=IFERROR(COUNTIFS('Bet Log'!$E$5:$E${BLAST},{crit},'Bet Log'!$K$5:$K${BLAST},\">0\")/COUNTIFS('Bet Log'!$E$5:$E${BLAST},{crit},'Bet Log'!$K$5:$K${BLAST},\"<>\"),\"\")").number_format='0.0%'
    hdr(ws,12,['Props by app','Legs','W','L','P','Leg win %','Entry profit ($)','Break-even (3-pick)',''])
    for i,a in enumerate(['Sleeper','Underdog','DraftKings'],13):
        ws.cell(row=i,column=1,value=a).font=B
        ws.cell(row=i,column=2,value=f"=COUNTIFS('Props Log'!$B$5:$B${PL},\"{a}\",'Props Log'!$J$5:$J${PL},\"?*\")")
        for j,res in ((3,'W'),(4,'L'),(5,'P')): ws.cell(row=i,column=j,value=f"=COUNTIFS('Props Log'!$B$5:$B${PL},\"{a}\",'Props Log'!$J$5:$J${PL},\"{res}\")")
        ws.cell(row=i,column=6,value=f'=IFERROR(C{i}/(C{i}+D{i}),"")').number_format='0.0%'
        ws.cell(row=i,column=7,value=f"=SUMIFS(Entries!$K$5:$K${EL},Entries!$B$5:$B${EL},\"{a}\")").number_format='$#,##0.00;($#,##0.00);-'
        ws.cell(row=i,column=8,value=f'=IFERROR(INDEX(Payouts!$D:$D,MATCH(1,INDEX((Payouts!$A:$A=A{i})*(Payouts!$B:$B=3),0),0)),0.524)').number_format='0.0%'
    hdr(ws,18,['Props by stat','Legs','W','L','P','Win %'])
    for i,s in enumerate(STATS,19):
        f_=FRIENDLY[s];ws.cell(row=i,column=1,value=f_).font=B
        ws.cell(row=i,column=2,value=f"=COUNTIFS('Props Log'!$E$5:$E${PL},\"{f_}\",'Props Log'!$J$5:$J${PL},\"?*\")")
        for j,res in ((3,'W'),(4,'L'),(5,'P')): ws.cell(row=i,column=j,value=f"=COUNTIFS('Props Log'!$E$5:$E${PL},\"{f_}\",'Props Log'!$J$5:$J${PL},\"{res}\")")
        ws.cell(row=i,column=6,value=f'=IFERROR(C{i}/(C{i}+D{i}),"")').number_format='0.0%'
    ws.cell(row=30,column=1,value='Total profit, all bets ($)').font=B;ws.cell(row=30,column=2,value='=G9+SUM(G13:G15)').number_format='$#,##0.00;($#,##0.00)'
    widths(ws,{'A':24,'B':8,'C':6,'D':6,'E':6,'F':9,'G':14,'H':14,'I':15})
    # ---- Ratings
    wr=wb.create_sheet('Ratings');title(wr,f'Team ratings through week {week-1}')
    hdr(wr,3,['Team','Off EPA/play','Def EPA/play allowed','Net','Plays/game','Prior off','Prior def','Returning off %','Talent','SP+'],40)
    for i,rt in enumerate(sorted(ratings,key=lambda r:-(r['off']-r['deff'])),4):
        for j,v in enumerate([rt['team'],rt['off'],rt['deff'],rt['off']-rt['deff'],rt['pace'],rt['pri_o'],rt['pri_d'],rt['ret'],rt['tal'],SP.get(rt['team'])],1):
            c=wr.cell(row=i,column=j,value=v)
            if j in (2,3,4,6,7): c.number_format='0.000'
            if j==5: c.number_format='0.0'
            if j==8: c.number_format='0%'
    widths(wr,{'A':22});wr.freeze_panes='B4'
    # ---- Key numbers
    wk=wb.create_sheet('Key Numbers');title(wk,f"Final margin frequency, FBS vs FBS 2021-2025 ({CONSTS['KEYN_N']} games)")
    hdr(wk,3,['Margin','% of games','Cumulative %'])
    for i,m in enumerate(range(0,36),4):
        wk.cell(row=i,column=1,value=m);c=wk.cell(row=i,column=2,value=CONSTS['KEYN'][str(m)]);c.number_format='0.0%'
        wk.cell(row=i,column=3,value=f'=SUM($B$4:B{i})').number_format='0.0%'
        if m in (3,7,10,14,17,21):
            for j in (1,2,3): wk.cell(row=i,column=j).fill=LEANF
    # ---- Backtest
    wt=wb.create_sheet('Backtest');title(wt,'Backtests (real data, CFBD)','Break-even at -110 = 52.4%.')
    blocks=[('Sides vs CLOSING line (out of sample 2024-25)',[['0-2 pts','47.1%'],['2-4','51.0%'],['4-7','50.8%'],['7+','51.3%'],['Verdict','No edge at closing numbers']]),
    ('Sides vs OPENING line (2022-25)',[['0-2 pts','51.9%, CLV +0.16'],['2-4','49.1%, CLV +0.12'],['4-7','51.1%, CLV +0.40'],['7+','53.2%, CLV +0.71'],['Verdict','Model moves WITH the market: bet sides early in the week']]),
    ('Totals vs CLOSING (out of sample 2024-25)',[['0-2 pts','51.4%'],['2-4','50.3%'],['4-7','55.8%'],['7+','~52%'],['Verdict','Best edge in the model: 4-7 pt totals edges']]),
    ('Totals vs OPENING (2022-25)',[['4-7 pts','53.1%, CLV +0.29'],['7+','56.3%, CLV +0.48']]),
    ('Props projections (2025 wks 5-14, 20,653 player-games)',[['Rush Yds MAE','30.5 vs 32.2 naive average'],['Rec Yds MAE','26.5 vs 27.9'],['Pass Yds MAE','70.0 vs 71.5'],['If line = projection: Rush Yds over hits','46.1% (Less wins 54%)'],['If line = projection: Rec Yds over hits','46.8% (Less wins 53%)'],['If line = projection: Pass Yds over hits','50.7%'],['Verdict','Yardage props are right-skewed. Lean Less on rush/rec yards unless the line is well below projection. Prop lines not backtested yet: the Props Log will do that.']]),
    ('Rest / bye weeks',[['Home off bye','51.2%: market prices it'],['Road off bye','49.5%: market prices it']])]
    r=3
    for t,rows in blocks:
        wt.cell(row=r,column=1,value=t).font=Font(name=AR,bold=True,size=12);r+=1
        for a,b_ in rows: wt.cell(row=r,column=1,value=a);wt.cell(row=r,column=2,value=b_);r+=1
        r+=1
    widths(wt,{'A':48,'B':80})
    # ---- How to update
    wh=wb.create_sheet('How To Update');title(wh,'Weekly routine')
    steps=[('Sunday/Monday','Send Claude: this workbook + cfb_engine.py + your CFBD key, and say "run week N". Engine grades last week, re-rates everyone, pulls opening lines. BET SIDES NOW (that is where side edges live).'),
    ('Tue-Thu','Update Injuries tab (QB news). Log bets in Bet Log as you place them (copy Game ID from Model).'),
    ('Friday','Paste or screenshot your Sleeper/Underdog boards (and any DK prop odds) to Claude, or type them into Props Board. Tiers show PLAY/LEAN/Pass.'),
    ('Saturday AM','Optional rerun for final lines + weather. Totals are the main play. Check wind column.'),
    ('After games','Enter results only if the engine did not. The next Sunday run auto-fills scores, closing lines, and prop actuals.'),
    ('Rules','Flat stakes (unit on Inputs). Never chase. Judge the model by CLV and 100+ bets, not one Saturday.'),
    ('API budget','Free CFBD tier = 1,000 calls/month. One weekly run uses ~35-50. Reset on the 1st.')]
    hdr(wh,3,['When','What'])
    for i,(a,b_) in enumerate(steps,4):
        wh.cell(row=i,column=1,value=a).font=B;c=wh.cell(row=i,column=2,value=b_);c.alignment=Alignment(wrap_text=True);wh.row_dimensions[i].height=32
    widths(wh,{'A':16,'B':120})
    order=['Best Bets','Season Dashboard','Props Board','Model','Projections','Bet Log','Props Log','Entries','Injuries','Inputs','Payouts','Ratings','Prop Dist','Key Numbers','Backtest','How To Update']
    wb._sheets=[wb[n] for n in order]
    wb.save(path);return picks
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--season',type=int,default=2026);ap.add_argument('--week',type=int,required=True)
    ap.add_argument('--prev',default=None);ap.add_argument('--cache',default=None);ap.add_argument('--out',default=None);a=ap.parse_args()
    out=a.out or f'CFB_Season_Model_{a.season}_wk{a.week}.xlsx'
    import pickle
    if a.cache and os.path.exists(a.cache): D=pickle.load(open(a.cache,'rb'))
    else:
        D=load(a.season,a.week)
        if a.cache: pickle.dump(D,open(a.cache,'wb'))
    games_wk,ratings,G=team_model(D,a.season,a.week)
    proj,cur=player_proj(D,a.season,a.week,games_wk);wx=weather(D,games_wk);prev=read_prev(a.prev)
    picks=build(out,a.season,a.week,D,games_wk,ratings,G,proj,cur,wx,prev)
    print(json.dumps(dict(out=out,games=len(games_wk),projections=len(proj),weather=len(wx),picks=[(p[0],p[1]['key'],p[3]) for p in picks],cfbd_calls=CALLS[0])))
if __name__=='__main__': main()
