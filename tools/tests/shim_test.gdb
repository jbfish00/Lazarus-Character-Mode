set pagination off
set confirm off
target remote :2345
python gdb.selected_inferior().write_memory(0x2032f00, bytes.fromhex("00c09fe51cff2fe181115f09"))
python gdb.selected_inferior().write_memory(0x2030000, bytes(6144))
set *(unsigned int*)0x3003664 = 0x2030000
break *0x81c40bc
break *0x81c4130
break *0x824aa54
echo \n=== CASE 0: flag off -> give ===\n
python gdb.selected_inferior().write_memory(0x2033000, bytes.fromhex("000000000000000000000000000000000000000200000000000000008e0000008e00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"))
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set *(unsigned char*)0x201b95d = 1
set $r0 = 0x2033000
set $sp = 0x03007F00
set $lr = 0x95f1181
set $pc = 0x2032f00
continue
printf "STOPPED_AT=%08x\n", $pc
echo \n=== CASE 1: party empty -> give (soft-lock guard) ===\n
python gdb.selected_inferior().write_memory(0x2033000, bytes.fromhex("000000000000000000000000000000000000000200000000000000008e0000008e00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"))
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set *(unsigned char*)0x201b95d = 0
set $r0 = 0x2033000
set $sp = 0x03007F00
set $lr = 0x95f1181
set $pc = 0x95f1180
continue
printf "STOPPED_AT=%08x\n", $pc
echo \n=== CASE 2: Red + Pikachu(25) -> give (on roster) ===\n
python gdb.selected_inferior().write_memory(0x2033000, bytes.fromhex("00000000000000000000000000000000000000020000000000000000190000001900000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"))
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set *(unsigned char*)0x201b95d = 1
set $r0 = 0x2033000
set $sp = 0x03007F00
set $lr = 0x95f1181
set $pc = 0x95f1180
continue
printf "STOPPED_AT=%08x\n", $pc
echo \n=== CASE 3: Red + Aerodactyl(142) -> PC (off roster) ===\n
python gdb.selected_inferior().write_memory(0x2033000, bytes.fromhex("000000000000000000000000000000000000000200000000000000008e0000008e00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"))
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set *(unsigned char*)0x201b95d = 1
set $r0 = 0x2033000
set $sp = 0x03007F00
set $lr = 0x95f1181
set $pc = 0x95f1180
continue
printf "STOPPED_AT=%08x\n", $pc
echo \n=== CASE 4: char 0 (unset) -> give ===\n
python gdb.selected_inferior().write_memory(0x2033000, bytes.fromhex("000000000000000000000000000000000000000200000000000000008e0000008e00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"))
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 0
set *(unsigned char*)0x201b95d = 1
set $r0 = 0x2033000
set $sp = 0x03007F00
set $lr = 0x95f1181
set $pc = 0x95f1180
continue
printf "STOPPED_AT=%08x\n", $pc
echo \n=== CASE 5: Red + Aerodactyl EGG -> give (eggs exempt) ===\n
python gdb.selected_inferior().write_memory(0x2033000, bytes.fromhex("000000000000000000000000000000000000000200000000000000008e4000008e00000000000000000000000000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000"))
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set *(unsigned char*)0x201b95d = 1
set $r0 = 0x2033000
set $sp = 0x03007F00
set $lr = 0x95f1181
set $pc = 0x95f1180
continue
printf "STOPPED_AT=%08x\n", $pc
echo \n=== CASE 6: char 192 out of range -> give ===\n
python gdb.selected_inferior().write_memory(0x2033000, bytes.fromhex("000000000000000000000000000000000000000200000000000000008e0000008e00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"))
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 192
set *(unsigned char*)0x201b95d = 1
set $r0 = 0x2033000
set $sp = 0x03007F00
set $lr = 0x95f1181
set $pc = 0x95f1180
continue
printf "STOPPED_AT=%08x\n", $pc
echo \n=== CASE 7: Blue + Aerodactyl -> give (their roster differs) ===\n
python gdb.selected_inferior().write_memory(0x2033000, bytes.fromhex("000000000000000000000000000000000000000200000000000000008e0000008e00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"))
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 3
set *(unsigned char*)0x201b95d = 1
set $r0 = 0x2033000
set $sp = 0x03007F00
set $lr = 0x95f1181
set $pc = 0x95f1180
continue
printf "STOPPED_AT=%08x\n", $pc
echo \n=== CASE 8: out-of-model species 1600 -> give (never block) ===\n
python gdb.selected_inferior().write_memory(0x2033000, bytes.fromhex("00000000000000000000000000000000000000020000000000000000400600004006000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"))
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set *(unsigned char*)0x201b95d = 1
set $r0 = 0x2033000
set $sp = 0x03007F00
set $lr = 0x95f1181
set $pc = 0x95f1180
continue
printf "STOPPED_AT=%08x\n", $pc
echo \n=== CASE 9: Red + species 1560 (max in-model, off roster) -> PC ===\n
python gdb.selected_inferior().write_memory(0x2033000, bytes.fromhex("00000000000000000000000000000000000000020000000000000000180600001806000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"))
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set *(unsigned char*)0x201b95d = 1
set $r0 = 0x2033000
set $sp = 0x03007F00
set $lr = 0x95f1181
set $pc = 0x95f1180
continue
printf "STOPPED_AT=%08x\n", $pc
echo \n=== TRADE 0: CM off, trade 0 -> allow ===\n
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 0
set *(unsigned short*)0x20055fc = 0
set *(unsigned short*)0x200560c = 0xDEAD
set $r0 = 0
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f1234
continue
printf "TRADE_RESULT=%04x\n", *(unsigned short*)0x200560c
echo \n=== TRADE 1: Red, trade 0 (#273) -> refuse ===\n
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set *(unsigned short*)0x20055fc = 0
set *(unsigned short*)0x200560c = 0xDEAD
set $r0 = 0
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f1234
continue
printf "TRADE_RESULT=%04x\n", *(unsigned short*)0x200560c
echo \n=== TRADE 2: Red, trade 1 (#311) -> refuse ===\n
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set *(unsigned short*)0x20055fc = 1
set *(unsigned short*)0x200560c = 0xDEAD
set $r0 = 0
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f1234
continue
printf "TRADE_RESULT=%04x\n", *(unsigned short*)0x200560c
echo \n=== TRADE 3: Red, trade 2 (#116) -> refuse ===\n
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set *(unsigned short*)0x20055fc = 2
set *(unsigned short*)0x200560c = 0xDEAD
set $r0 = 0
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f1234
continue
printf "TRADE_RESULT=%04x\n", *(unsigned short*)0x200560c
echo \n=== TRADE 4: Red, trade 3 (Meowth) -> allow ===\n
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set *(unsigned short*)0x20055fc = 3
set *(unsigned short*)0x200560c = 0xDEAD
set $r0 = 0
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f1234
continue
printf "TRADE_RESULT=%04x\n", *(unsigned short*)0x200560c
echo \n=== TRADE 5: Red, trade idx 7 out of range -> allow ===\n
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set *(unsigned short*)0x20055fc = 7
set *(unsigned short*)0x200560c = 0xDEAD
set $r0 = 0
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f1234
continue
printf "TRADE_RESULT=%04x\n", *(unsigned short*)0x200560c
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x0
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
set *(unsigned char*)0x2031410 = 0x20
set *(unsigned short*)0x20315d4 = 1
set $r0 = 142
set $r1 = 30
set $sp = 0x03007F00
set $lr = 0x81c40bd
set $pc = 0x95f13cc
continue
printf "WILD_RESULT=%d,%d\n", $r0, $r1
disconnect
quit
