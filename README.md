Frisbee Lite CLI 使い方ガイド
インストール
bash# PyUSBのインストール
pip install pyusb

# スクリプトを保存
chmod +x frisbee_lite_cli.py
基本的な使い方
1. ヘルプの表示
bashpython frisbee_lite_cli.py --help
2. デバイスへの接続確認
まず、接続したいUSBデバイスのVID/PIDを確認します：
bash# lsusbコマンドで確認
lsusb

# 例: Bus 001 Device 005: ID 05ac:1297 Apple, Inc. iPhone
# VID: 0x05ac, PID: 0x1297
3. シングルショットモード（1回のコントロール転送）
bash# 基本的なGET_DESCRIPTOR要求
python frisbee_lite_cli.py \
  --vid 0x05ac \
  --pid 0x1297 \
  --single \
  --bmRequestType 0x80 \
  --bRequest 0x06 \
  --wValue 0x0100 \
  --wIndex 0x0000 \
  --wLength 0x0012
```

**出力例：**
```
[SUCCESS] Connected to device (VID: 0x05ac, PID: 0x1297)

2024/12/17 10:30:45
  bmRequestType: 0x80
  bRequest: 0x06
  wValue: 0x0100
  wIndex: 0x0000
  wLength: 0x0012
  Received: array('B', [18, 1, 0, 2, 0, 0, 0, 64, 172, 5, 151, 18, ...])
ファジングモード
4. bRequestをファジング（0x00～0xff）
bashpython frisbee_lite_cli.py \
  --vid 0x05ac \
  --pid 0x1297 \
  --fuzz \
  --bmRequestType 0x80 \
  --bRequest-start 0x00 \
  --bRequest-end 0xff \
  --bRequest-fuzz \
  --wValue 0x0000 \
  --wIndex 0x0000 \
  --wLength 0x0008
5. 複数パラメータを同時にファジング
bash# bmRequestTypeとbRequestを同時にファジング
python frisbee_lite_cli.py \
  --vid 0x05ac \
  --pid 0x1297 \
  --fuzz \
  --bmRequestType-start 0x80 \
  --bmRequestType-end 0x81 \
  --bmRequestType-fuzz \
  --bRequest-start 0x00 \
  --bRequest-end 0xff \
  --bRequest-fuzz \
  --wValue 0x0000 \
  --wIndex 0x0000 \
  --wLength 0x0008
6. wValueの範囲をファジング
bashpython frisbee_lite_cli.py \
  --vid 0x05ac \
  --pid 0x1297 \
  --fuzz \
  --bmRequestType 0x80 \
  --bRequest 0x06 \
  --wValue-start 0x0100 \
  --wValue-end 0x0300 \
  --wValue-fuzz \
  --wIndex 0x0000 \
  --wLength 0x0012
7. 全パラメータをファジング（注意：時間がかかります）
bashpython frisbee_lite_cli.py \
  --vid 0x05ac \
  --pid 0x1297 \
  --fuzz \
  --bmRequestType-start 0x80 \
  --bmRequestType-end 0x83 \
  --bmRequestType-fuzz \
  --bRequest-start 0x00 \
  --bRequest-end 0x0f \
  --bRequest-fuzz \
  --wValue-start 0x0000 \
  --wValue-end 0x00ff \
  --wValue-fuzz \
  --wIndex-start 0x0000 \
  --wIndex-end 0x00ff \
  --wIndex-fuzz \
  --wLength 0x0008
ログファイル
8. カスタムログファイルを指定
bashpython frisbee_lite_cli.py \
  --vid 0x05ac \
  --pid 0x1297 \
  --fuzz \
  --bRequest-start 0x00 \
  --bRequest-end 0xff \
  --bRequest-fuzz \
  --bmRequestType 0x80 \
  --wValue 0x0000 \
  --wIndex 0x0000 \
  --wLength 0x0008 \
  --log my_fuzz_test.txt
デフォルトでは FrisbeeLite_logfile_YYYY-MM-DD.txt に保存されます。
実用例
デバイスディスクリプタの取得
bashpython frisbee_lite_cli.py \
  --vid 0x05ac --pid 0x1297 \
  --single \
  --bmRequestType 0x80 \
  --bRequest 0x06 \
  --wValue 0x0100 \
  --wIndex 0x0000 \
  --wLength 0x0012
コンフィギュレーションディスクリプタの取得
bashpython frisbee_lite_cli.py \
  --vid 0x05ac --pid 0x1297 \
  --single \
  --bmRequestType 0x80 \
  --bRequest 0x06 \
  --wValue 0x0200 \
  --wIndex 0x0000 \
  --wLength 0x0009
ベンダー固有リクエストのファジング
bashpython frisbee_lite_cli.py \
  --vid 0x05ac --pid 0x1297 \
  --fuzz \
  --bmRequestType 0xc0 \
  --bRequest-start 0x00 \
  --bRequest-end 0xff \
  --bRequest-fuzz \
  --wValue 0x0000 \
  --wIndex 0x0000 \
  --wLength 0x0040
重要な注意事項
⚠️ 安全性

隔離された環境で実行: 本番環境では使用しないでください
デバイスの損傷: ファジングによりデバイスが応答しなくなる可能性があります
権限: USB操作には通常rootまたはsudo権限が必要です

sudo権限での実行
bashsudo python frisbee_lite_cli.py --vid 0x05ac --pid 0x1297 --single ...
```

### 中断方法

ファジング中に `Ctrl+C` を押すと安全に停止します：
```
^C
[INFO] Fuzzing interrupted by user

[INFO] Fuzzing completed
[INFO] Total tests: 1523
[INFO] Successful: 234
[INFO] Failed: 1289
[INFO] Results saved to: FrisbeeLite_logfile_2024-12-17.txt
パラメータ説明
パラメータ説明値の範囲bmRequestTypeリクエストタイプ0x00-0xffbRequestリクエスト番号0x00-0xffwValue値フィールド0x0000-0xffffwIndexインデックスフィールド0x0000-0xffffwLengthデータ長0x0000-0xffff
bmRequestTypeの構成

Bit 7: データ転送方向（0=Host to Device, 1=Device to Host）
Bit 6-5: タイプ（0=標準, 1=クラス, 2=ベンダー）
Bit 4-0: 受信者（0=デバイス, 1=インターフェース, 2=エンドポイント）

例：

0x80: Device to Host, Standard, Device
0xc0: Device to Host, Vendor, Device
0x21: Host to Device, Class, Interface

トラブルシューティング
デバイスが見つからない
bash# デバイスの確認
lsusb

# udevルールの設定（Linux）
sudo nano /etc/udev/rules.d/99-usb.rules
# 追加: SUBSYSTEM=="usb", ATTR{idVendor}=="05ac", MODE="0666"

sudo udevadm control --reload-rules
権限エラー
bash# sudoで実行
sudo python frisbee_lite_cli.py ...

# または自分をusbグループに追加
sudo usermod -a -G plugdev $USER