#!/usr/bin/env python3
"""
Frisbee Lite CLI - USB Device Fuzzer
Command-line version without wxPython
"""

import usb.core
import usb.util
import sys
import time
import argparse
from datetime import datetime


class USBFuzzer:
    def __init__(self, vid, pid):
        self.vid = vid
        self.pid = pid
        self.dev = None
        self.fuzzing = False
        
    def connect(self):
        """Connect to USB device"""
        self.dev = usb.core.find(idVendor=self.vid, idProduct=self.pid)
        
        if self.dev is None:
            print(f"[ERROR] Device not found (VID: 0x{self.vid:04x}, PID: 0x{self.pid:04x})")
            return False
        
        try:
            # カーネルドライバがアクティブな場合はデタッチ
            if self.dev.is_kernel_driver_active(0):
                print("[INFO] Detaching kernel driver...")
                try:
                    self.dev.detach_kernel_driver(0)
                    print("[SUCCESS] Kernel driver detached")
                except usb.core.USBError as e:
                    print(f"[WARNING] Could not detach kernel driver: {e}")
                    print("[INFO] Trying to continue anyway...")
            
            # デバイスをリセット（オプション）
            try:
                self.dev.reset()
                print("[INFO] Device reset successful")
            except usb.core.USBError as e:
                print(f"[WARNING] Device reset failed: {e}")
            
            # コンフィギュレーションを設定
            self.dev.set_configuration()
            print(f"[SUCCESS] Connected to device (VID: 0x{self.vid:04x}, PID: 0x{self.pid:04x})")
            return True
            
        except usb.core.USBError as e:
            print(f"[ERROR] Failed to configure device: {e}")
            return False
    
    def single_shot(self, bmRequestType, bRequest, wValue, wIndex, wLength):
        """Send single control transfer"""
        if not self.dev:
            if not self.connect():
                return None
        
        timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        print(f"\n{timestamp}")
        print(f"  bmRequestType: 0x{bmRequestType:02x}")
        print(f"  bRequest: 0x{bRequest:02x}")
        print(f"  wValue: 0x{wValue:04x}")
        print(f"  wIndex: 0x{wIndex:04x}")
        print(f"  wLength: 0x{wLength:04x}")
        
        try:
            recv = self.dev.ctrl_transfer(
                bmRequestType, bRequest, wValue, wIndex, wLength
            )
            print(f"  Received: {repr(recv)}")
            return recv
        except Exception as e:
            print(f"  [ERROR] {e}")
            return None
    
    def fuzz(self, bmRequestType_start, bmRequestType_end, bmRequestType_fuzz,
             bRequest_start, bRequest_end, bRequest_fuzz,
             wValue_start, wValue_end, wValue_fuzz,
             wIndex_start, wIndex_end, wIndex_fuzz,
             wLength, log_file=None):
        """Fuzz USB device with specified parameters"""
        
        if not self.dev:
            if not self.connect():
                return
        
        # Open log file
        if log_file is None:
            log_file = f"FrisbeeLite_logfile_{datetime.now().strftime('%Y-%m-%d')}.txt"
        
        with open(log_file, 'a') as fp:
            fp.write(f"\n\n**** FrisbeeLite - Fuzzing started at {datetime.now()} ****\n\n")
        
        print(f"\n[INFO] Starting fuzzing session...")
        print(f"[INFO] Log file: {log_file}")
        
        self.fuzzing = True
        total_tests = 0
        successful_tests = 0
        
        bmRequestType = bmRequestType_start
        while bmRequestType <= bmRequestType_end:
            if not self.fuzzing:
                break
                
            bRequest = bRequest_start
            while bRequest <= bRequest_end:
                if not self.fuzzing:
                    break
                    
                wValue = wValue_start
                while wValue <= wValue_end:
                    if not self.fuzzing:
                        break
                        
                    wIndex = wIndex_start
                    while wIndex <= wIndex_end:
                        if not self.fuzzing:
                            break
                        
                        total_tests += 1
                        timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                        
                        # Progress indicator
                        if total_tests % 100 == 0:
                            print(f"\r[PROGRESS] Tests: {total_tests}, Successful: {successful_tests}", end='', flush=True)
                        
                        # Log to file
                        with open(log_file, 'a') as fp:
                            fp.write(f"{timestamp}    ")
                            fp.write(f"bmRequestType: 0x{bmRequestType:02x} ")
                            fp.write(f"bRequest: 0x{bRequest:02x} ")
                            fp.write(f"wValue: 0x{wValue:04x} ")
                            fp.write(f"wIndex: 0x{wIndex:04x} ")
                            fp.write(f"wLength: 0x{wLength:04x}\n")
                        
                        # Send control transfer
                        try:
                            recv = self.dev.ctrl_transfer(
                                bmRequestType, bRequest, wValue, wIndex, wLength
                            )
                            successful_tests += 1
                            
                            with open(log_file, 'a') as fp:
                                fp.write(f"Received: {repr(recv)}\n")
                                
                        except KeyboardInterrupt:
                            self.fuzzing = False
                            print("\n[INFO] Fuzzing interrupted by user")
                            break
                        except Exception as e:
                            with open(log_file, 'a') as fp:
                                fp.write(f"Error: {str(e)}\n")
                        
                        if not wIndex_fuzz:
                            break
                        wIndex += 1
                    
                    if not wValue_fuzz:
                        break
                    wValue += 1
                
                if not bRequest_fuzz:
                    break
                bRequest += 1
            
            if not bmRequestType_fuzz:
                break
            bmRequestType += 1
        
        self.fuzzing = False
        print(f"\n\n[INFO] Fuzzing completed")
        print(f"[INFO] Total tests: {total_tests}")
        print(f"[INFO] Successful: {successful_tests}")
        print(f"[INFO] Failed: {total_tests - successful_tests}")
        print(f"[INFO] Results saved to: {log_file}")
        
        with open(log_file, 'a') as fp:
            fp.write(f"\n**** Fuzzing completed - Total: {total_tests}, Successful: {successful_tests} ****\n")
    
    def stop_fuzzing(self):
        """Stop fuzzing operation"""
        self.fuzzing = False
        print("\n[INFO] Stopping fuzzing...")


def main():
    parser = argparse.ArgumentParser(
        description='Frisbee Lite - USB Device Fuzzer (CLI Version)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single control transfer
  %(prog)s --vid 0x05ac --pid 0x1297 --single \\
    --bmRequestType 0x80 --bRequest 0x06 --wValue 0x0100 --wIndex 0x0000 --wLength 0x0012
  
  # Fuzz bRequest values
  %(prog)s --vid 0x05ac --pid 0x1297 --fuzz \\
    --bmRequestType 0x80 --bRequest-start 0x00 --bRequest-end 0xff --bRequest-fuzz \\
    --wValue 0x0000 --wIndex 0x0000 --wLength 0x0008
  
  # Full fuzzing with multiple parameters
  %(prog)s --vid 0x05ac --pid 0x1297 --fuzz \\
    --bmRequestType-start 0x80 --bmRequestType-end 0x81 --bmRequestType-fuzz \\
    --bRequest-start 0x00 --bRequest-end 0xff --bRequest-fuzz \\
    --wValue-start 0x0000 --wValue-end 0x0100 --wValue-fuzz \\
    --wIndex 0x0000 --wLength 0x0008
        """
    )
    
    # Device selection
    parser.add_argument('--vid', type=lambda x: int(x, 0), required=True,
                        help='Vendor ID (hex format: 0x05ac)')
    parser.add_argument('--pid', type=lambda x: int(x, 0), required=True,
                        help='Product ID (hex format: 0x1297)')
    
    # Operation mode
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--single', action='store_true',
                      help='Single control transfer mode')
    mode.add_argument('--fuzz', action='store_true',
                      help='Fuzzing mode')
    mode.add_argument('--gui', action='store_true',
                      help='Launch GUI mode')
    
    # Control transfer parameters
    parser.add_argument('--bmRequestType', type=lambda x: int(x, 0), default=0x80)
    parser.add_argument('--bmRequestType-start', type=lambda x: int(x, 0), default=0x00)
    parser.add_argument('--bmRequestType-end', type=lambda x: int(x, 0), default=0xff)
    parser.add_argument('--bmRequestType-fuzz', action='store_true')
    
    parser.add_argument('--bRequest', type=lambda x: int(x, 0), default=0x06)
    parser.add_argument('--bRequest-start', type=lambda x: int(x, 0), default=0x00)
    parser.add_argument('--bRequest-end', type=lambda x: int(x, 0), default=0xff)
    parser.add_argument('--bRequest-fuzz', action='store_true')
    
    parser.add_argument('--wValue', type=lambda x: int(x, 0), default=0x0000)
    parser.add_argument('--wValue-start', type=lambda x: int(x, 0), default=0x0000)
    parser.add_argument('--wValue-end', type=lambda x: int(x, 0), default=0xffff)
    parser.add_argument('--wValue-fuzz', action='store_true')
    
    parser.add_argument('--wIndex', type=lambda x: int(x, 0), default=0x0000)
    parser.add_argument('--wIndex-start', type=lambda x: int(x, 0), default=0x0000)
    parser.add_argument('--wIndex-end', type=lambda x: int(x, 0), default=0xffff)
    parser.add_argument('--wIndex-fuzz', action='store_true')
    
    parser.add_argument('--wLength', type=lambda x: int(x, 0), default=0x0012)
    
    # Output
    parser.add_argument('--log', type=str, default=None,
                        help='Log file path (default: FrisbeeLite_logfile_YYYY-MM-DD.txt)')
    
    args = parser.parse_args()
    
    # Create fuzzer instance
    fuzzer = USBFuzzer(args.vid, args.pid)
    
    try:
        if args.single:
            # Single shot mode
            fuzzer.single_shot(
                args.bmRequestType,
                args.bRequest,
                args.wValue,
                args.wIndex,
                args.wLength
            )
            
        elif args.fuzz:
            # Fuzzing mode
            fuzzer.fuzz(
                args.bmRequestType_start if args.bmRequestType_fuzz else args.bmRequestType,
                args.bmRequestType_end if args.bmRequestType_fuzz else args.bmRequestType,
                args.bmRequestType_fuzz,
                args.bRequest_start if args.bRequest_fuzz else args.bRequest,
                args.bRequest_end if args.bRequest_fuzz else args.bRequest,
                args.bRequest_fuzz,
                args.wValue_start if args.wValue_fuzz else args.wValue,
                args.wValue_end if args.wValue_fuzz else args.wValue,
                args.wValue_fuzz,
                args.wIndex_start if args.wIndex_fuzz else args.wIndex,
                args.wIndex_end if args.wIndex_fuzz else args.wIndex,
                args.wIndex_fuzz,
                args.wLength,
                args.log
            )
            
        elif args.gui:
            # Launch GUI
            print("[INFO] Launching GUI mode...")
        #     from frisbee_lite_gui import launch_gui
        #     launch_gui(args.vid, args.pid)
            
    except KeyboardInterrupt:
        print("\n[INFO] Operation cancelled by user")
        fuzzer.stop_fuzzing()
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()