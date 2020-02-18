import os
import linecache
import time
import Queue
import threading
import sys
import socket

def spectrum_sense():
    os.system("/root/USRP/gnuradio/gr-uhd/examples/python/usrp_spectrum_sense.py  -s 2000000 -b 1000000 0.869G 0.894G > /tmp/output.txt")



try:
    t = threading.Thread(target=spectrum_sense, args = ())
    t.daemon = True
    t.start()
  

    time.sleep(30) #for spectrum sensing purposes

    freq_list = []
    optimal_window = []

    with open("/tmp/output.txt", 'r') as f:
      for i in range(22, 100):  #line in enumerate(f, 22): #for x in range(0, 3):
        line = linecache.getline("/tmp/output.txt", i)
        if(line):
         signal = line[77:81]
         noise = line[-14:-1]
         freq_status = [line[56:67], signal, noise]
         freq_list.append(freq_status)

    for i in range(0, 5):
        optimal_window.append(freq_list[i])
    #print(optimal_window) 
   
    time.sleep(10)
    #mean values
    sum_sig = []
    sum_noise = []
    for i in range(0, 5):
         sum_sig.append(float(optimal_window[i][1]))
         sum_noise.append(float(optimal_window[i][2]))
    signal_mean_value_level = sum(sum_sig)/len(sum_sig)
    noise_mean_value_level = sum(sum_noise)/len(sum_noise)

    #variances
    variance_sig_sum = []
    variance_noise_sum = [] 
    for i in range(0, 5):
         variance_sig_sum.append(abs(sum_sig[i] - signal_mean_value_level))
         variance_noise_sum.append(abs(sum_noise[i] - noise_mean_value_level))
    signal_variance = sum(variance_sig_sum) / len(sum_sig)
    noise_variance  = sum(variance_noise_sum) / len(sum_noise)

    #total optimization rule (50% signal presense mean value, 30% variance of signal presense, 15% noise presense mean value, 5% variance of noise presense)
    opt_rule = (0.5 * signal_mean_value_level) + (0.3 * signal_variance) + (0.15 * noise_mean_value_level) + (0.05 * noise_variance)

    temp_optimal_window = optimal_window[:]
    for i in range(5, len(freq_list)):  #line in enumerate(f, 22): #for x in range(0, 3):
         print(i)
         print(opt_rule)
         temp_optimal_window.remove(temp_optimal_window[0]) #del temp_optimal_window[0]
         temp_optimal_window.append(freq_list[i])
         print(temp_optimal_window[2][0])
         #mean values
         temp_sum_sig = []
         temp_sum_noise = []
         for i in range(0, 5):
             temp_sum_sig.append(float(temp_optimal_window[i][1]))
             temp_sum_noise.append(float(temp_optimal_window[i][2]))
         temp_signal_mean_value_level = sum(temp_sum_sig)/len(temp_sum_sig)
         temp_noise_mean_value_level = sum(temp_sum_noise)/len(temp_sum_noise)
         #variances
         temp_variance_sig_sum = []
         temp_variance_noise_sum = []
         for i in range(0, 5):
             temp_variance_sig_sum.append(abs(temp_sum_sig[i] - temp_signal_mean_value_level))
             temp_variance_noise_sum.append(abs(temp_sum_noise[i] - temp_noise_mean_value_level))
         temp_signal_variance = sum(temp_variance_sig_sum) / len(temp_sum_sig)
         temp_noise_variance  = sum(temp_variance_noise_sum) / len(temp_sum_noise)
         #total optimization rule (50% signal presense mean value, 30% variance of signal presense, 15% noise presense mean value, 5% variance of noise presense)
         temp_opt_rule = (0.5 * temp_signal_mean_value_level) + (0.3 * temp_signal_variance) + (0.15 * temp_noise_mean_value_level) + (0.05 * temp_noise_variance)
         print(temp_opt_rule)
         #check for optimal window
         if  temp_opt_rule < opt_rule:
             opt_rule = temp_opt_rule
             optimal_window = []
             optimal_window = temp_optimal_window[:]
             print("opt window", optimal_window)
         else:
             print("discarded")
             print("\n")

    print("ideal frequency is ", optimal_window[2][0])

    with open("rel7763/targets/bin/enb.band13.rel10.exmimo2.conf", 'r') as f:
        line0 = linecache.getline("rel7763/targets/bin/enb.band13.rel10.exmimo2.conf", 31)
        line1 = line0.replace(line0[64:73], optimal_window[2][0][:-2])
        lines = f.readlines()
    with open("rel7763/targets/bin/enb.band13.rel10.exmimo2.conf", 'w') as f:
        for line in lines:
           if line == line0:
             f.write(line1)
             print(line)
           else:
               f.write(line)
    #socket utitlities
    TCP_IP = '10.64.44.56'
    TCP_PORT = 5005
    BUFFER_SIZE = 1024 
    MESSAGE = optimal_window[2][0]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(MESSAGE)
    data = s.recv(BUFFER_SIZE)
    s.close()

    print "sent data:", data
    #socket utilities


    os.system("killall -9 python")
    sys.exit
except (KeyboardInterrupt, SystemExit):
#    cleanup_stop_thread();
    os.system("killall -9 python")
    sys.exit()




