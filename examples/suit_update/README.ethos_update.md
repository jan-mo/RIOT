# Update over ethos

This example was modified to demonstrate a improved update process, by reducing the payload with the heatshrink algorithm. Further calculating the difference between two firmware.

## commands for execution

Run the ethos console:
```
	sudo ./dist/tools/ethos/start_network.sh /dev/ttyACM0 riot0 2001:db8::/64
	sudo ip address add 2001:db8::1/128 dev riot0 && ifconfig
```

Start the CoAP server
```
	mkdir coaproot
	aiocoap-fileserver /coaproot
```

publish the NORMAL update:
```
	sudo SUIT_COAP_SERVER=[2001:db8::1] make -j suit/publish
	SUIT_COAP_SERVER=[2001:db8::1] SUIT_CLIENT=[fe80::a48b:b4ff:fec9:e58d%riot0] make -j suit/notify
```

make and publish the IMPROVED update process:
```
	sudo make -j flash && sudo ./mark_installed_version.py
	sudo SUIT_COAP_SERVER=[2001:db8::1] make -j suit/publish && sudo ./manual_diff.py && SUIT_COAP_SERVER=[2001:db8::1] SUIT_CLIENT=[fe80::a48b:b4ff:fec9:e58d%riot0] make -j suit/notify
```
