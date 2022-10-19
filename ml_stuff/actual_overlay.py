#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import numpy as np
import pynq.lib.dma
from pynq import allocate
from pynq import Overlay
# import time

overlay = Overlay('mlp.bit')
    
dma_send = overlay.axi_dma_0
dma_recv = overlay.axi_dma_0

input_buffer = allocate(shape=(60,), dtype=np.float32)
output_buffer = allocate(shape=(1,), dtype=np.int32)

test_input_memory = [-0.599470000000000, 0.928630000000000, 0.001622564102564, 0.004120000000000, 0.082677622282726, 0.063280000000000, 3.735590765966022, 1.576600355907922, 1.312455042830961, 0.673451630886567, -0.468090000000000, 0.660380000000000, 0.001685384615385, 0.013740000000000, 0.055123745951822, 0.065730000000000, 2.607283514157983, 1.273712969903649, 1.234494402434771, 0.484901775662363, -0.463590000000000, 0.875190000000000, -0.002243333333333, -0.029620000000000, 0.066550919028070, 0.087490000000000, 3.350365003376681, 1.340362991318738, 1.162036236514788, 0.751836092324218, -0.205200000000000, 0.183960000000000, -0.001753589743590, -0.005620000000000, 0.008021157865722, 0.006355053107567, 0.887876734811813, 0.484330080812356, 0.561758974614014, 0.072199570765567, -0.268920000000000, 0.258540000000000, -0.021042051282051, -0.011840000000000, 0.011617022985155, 0.040287699628622, 1.924614487514040, 0.539810932622794, 0.412088668012489, 0.171722110458302, -0.133420000000000, 0.220580000000000, 0.002670000000000, -0.001340000000000, 0.005134758584211, 0.042805588082785, 1.125095066533663, 0.344601080504714, 0.250290916319209, 0.078666026210115,
	-0.203740000000000,0.220000000000000,-0.000344000000000,0.005685000000000,0.005673331988718,0.013760000000000,0.987697656674349,0.397867392705730,0.321928676932263,0.064580737252866,-0.282440000000000,0.168630000000000,0.000977000000000,0.005155000000000,0.006722100154872,0.039080000000000,1.124489046300704,0.441836467429218,0.408829453378462,0.068698075127866,-0.068700000000000,0.045500000000000,-0.002540250000000,0.000995000000000,0.000587770223013,0.059417809313264,0.324068211274065,0.137145119631010,0.121183144600168,0.004484481703996,-0.065920000000000,0.059330000000000,-0.002512000000000,-0.002690000000000,0.000644578483077,0.027677371905769,0.344820180104532,0.139782691995771,0.122776713526588,0.006001810890682,-0.056030000000000,0.034180000000000,-0.009381000000000,-0.003115000000000,0.000424193870769,0.021874774700646,0.382752578430088,0.108959070344852,0.079173510503057,0.008401649630344,-0.100220000000000,0.104610000000000,0.006661000000000,0.004520000000000,0.001195204065641,0.042900322414485,0.443883972894776,0.187163039506646,0.158821150532121,0.013700217479624,
	-0.169390000000000, 0.207330000000000, 0.002231388888889, 0.001220000000000, 0.003541678829444, 0.080330000000000, 0.590980133354079, 0.322082524878281, 0.334856670170577, 0.020983735201404, -0.215730000000000, 0.172750000000000, 0.010618333333333, 0.006870000000000, 0.005405036837143, 0.042200000000000, 0.733533682508407, 0.402748925434818, 0.368083993926047, 0.031915086645703, -0.267180000000000, 0.198850000000000, -0.001423055555556, -0.001640000000000, 0.007291574393254, 0.019190000000000, 1.243283136865318, 0.393057035158836, 0.318770399569066, 0.103663721841064, -0.112790000000000, 0.091800000000000, 0.003696111111111, 0.002445000000000, 0.001364652658730, 0.053437770220087, 0.484969299721739, 0.193473670981316, 0.158382855448435, 0.011131802986643, -0.089360000000000, 0.030640000000000, -0.018161666666667, -0.006895000000000, 0.000869170762857, 0.012449790778637, 0.653820000000000, 0.138672133060698, 0.086921585981546, 0.023724490744179, -0.044070000000000, 0.069700000000000, -0.001746666666667, -0.000610000000000, 0.000388585348571, 0.009140000000000, 0.241894450933418, 0.099561098043138, 0.092141059134777, 0.003906416938057,
	-0.053050000000000,0.058020000000000,0.001786052631579,0.003855000000000,0.000819569359673,0.010190000000000,0.322502439406022,0.147163350086656,0.128588361765488,0.009025753931577,-0.120690000000000,0.097020000000000,0.002143421052632,0.011530000000000,0.001804479136629,0.039170000000000,0.456212497703116,0.232194640421295,0.238558181832636,0.013378011596372,-0.115500000000000,0.079010000000000,0.001345000000000,0.003360000000000,0.001548106695946,0.010310000000000,0.503395087049578,0.189941285236101,0.148510632258531,0.021845890724017,-0.034550000000000,0.050170000000000,-0.000115789473684,0.000670000000000,0.000260051225036,0.004400000000000,0.175406364194596,0.086936754020454,0.080400624040793,0.002120200346343,-0.050170000000000,0.034420000000000,-0.000070526315789,0.001035000000000,0.000268555799716,0.002680000000000,0.192482370565038,0.084542153073190,0.070280648176748,0.002864766547094,-0.022830000000000,0.032960000000000,0.000758421052632,0.002440000000000,0.000154042419061,0.003640000000000,0.170941665629513,0.064510351758408,0.053883532754197,0.001601999600223,
	-0.212060000000000, 0.282370000000000, 0.002985250000000, -0.008855000000000, 0.013345287707628, 0.119410000000000, 2.087030000000000, 0.624239634852148, 0.601786988328689, 0.134510325722725, -0.353820000000000, 0.425570000000000, -0.020258000000000, -0.023475000000000, 0.024583295385641, 0.095846609978652, 2.289709691109117, 0.845151236366699, 0.846753248731468, 0.267572687454196, -0.292140000000000, 0.118400000000000, 0.002746000000000, 0.004695000000000, 0.006203370557949, 0.088671019840121, 0.968664886857709, 0.432797877041113, 0.403297213682402, 0.056327251311493, -0.067870000000000, 0.107060000000000, -0.003234750000000, -0.001100000000000, 0.001597662625577, 0.038043973349761, 0.526130000000000, 0.209311346305799, 0.189490179683896, 0.019401176418106, -0.084350000000000, 0.065920000000000, -0.007164500000000, -0.001400000000000, 0.001360045533077, 0.062509771842266, 0.524616700952427, 0.200977429057045, 0.164622408871804, 0.015080052522688, -0.097410000000000, 0.118770000000000, -0.010403500000000, -0.004635000000000, 0.002149909910513, 0.029463988760243, 0.606155206898716, 0.254331514468886, 0.191083654299907, 0.024093620254321,
	-0.237330000000000, 0.205340000000000, 0.010244571428571, 0.017480000000000, 0.008802084302017, 0.199996916957431, 1.062131410773568, 0.488253757170773, 0.389550068273630, 0.066451029244171, -0.201370000000000, 0.426560000000000, -0.014951428571429, -0.017560000000000, 0.011837015553782, 0.221120881532642, 0.991398949837363, 0.597822668599523, 0.598922223627690, 0.054446276199973, -0.037940000000000, 0.106110000000000, 0.000957714285714, 0.000690000000000, 0.000755777747563, 0.014934803429305, 0.278570051638523, 0.139157778254727, 0.155667006843812, 0.006550825185067, -0.064210000000000, 0.062740000000000, -0.006423714285714, -0.006100000000000, 0.000851388594622, 0.035363539502167, 0.342249715892135, 0.153395424268794, 0.172284428909894, 0.007063102646144, -0.094360000000000, 0.077270000000000, -0.003794285714286, 0.001340000000000, 0.001260374731092, 0.013550661443815, 0.429244454006816, 0.181046507410368, 0.171278336805907, 0.010889924864934, -0.084590000000000, 0.082280000000000, -0.008147142857143, -0.001950000000000, 0.001138064232773, 0.052387080586995, 0.347007632513366, 0.185833848697725, 0.193751335955180, 0.006673802448138]
expected_memory = [0, 3, 1, 4, 2, 2]

success_count = 0
element_count = 0

for i in range(6):
	for j in range(60):
		input_buffer[j] = float(test_input_memory[element_count])
		element_count += 1
	print("Sending input buffer")    
# 	print(input_buffer)
# 	start = time.time()
	dma_send.sendchannel.transfer(input_buffer)
	print("Receiving output buffer")    
	dma_recv.recvchannel.transfer(output_buffer)
# 	end = time.time()
#	print(output_buffer)    
	dma_send.sendchannel.wait()
	dma_recv.recvchannel.wait()
	print("Case number " + str(i+1) + ":")
	print("Expected: " + str(expected_memory[i]))
	print("Output: " , int(output_buffer[0]))
	if (output_buffer[0] == expected_memory[i]):
		success_count += 1
		print("Case number "+ str(i+1) + ": Passed")
	else:
		print("Case number "+ str(i+1) + ": Failed")    
        
print("Accuracy:" + str(success_count/6))
print("Time between sending and receiving bufer: ", end - start)


# In[ ]:




