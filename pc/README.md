# Shuncar 操縦用PC用プログラム

## 対応コントローラー一覧

以下のコントローラーで動作を確認しています。
これらのコントローラを接続すると、自動で認識してキー配列を設定します。

- SHANWAN JC-U4013S DirectInput Mode ([amazon](https://www.amazon.co.jp/dp/B01N1S3YJP/))
- HORI Racing Wheel Apex ([amazon](https://www.amazon.co.jp/dp/B09P9S5JJ1/))

以下のキーボードに関しては、特殊な操作を行う必要があります。

- Logicool G G29 Driving Force ([amazon](https://www.amazon.co.jp/dp/B00ZQNBTJW/))

### 環境構築（UV対応）

1. Pythonのバージョン管理ツールである[UV](https://github.com/astral-sh/uv)をインストールします。

   MacとLinuxの場合

   ```
   # On macOS and Linux.
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   Windowsの場合

   ```
   # On Windows.
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. hidapiのインストール (mac / linuxの場合)

   ```
   brew install hidapi # mac
   sudo apt install libhidapi-dev # Debian系
   ```

3. UV環境の同期をします。必要Pythonバージョンがない場合は自動でダウンロードされ依存環境も自動でダウンロードされます。（インターネットが必要です）

   ```
   PS:> cd pc && uv sync
   Using CPython 3.12.12
   Creating virtual environment at: .venv
   Resolved 12 packages in 0.85ms
   Installed 11 packages in 80ms
    + certifi==2025.10.5
    + charset-normalizer==3.4.4
    + g29py==0.0.10
    + hid==1.0.4
    + idna==3.11
    + ifaddr==0.2.0
    + pygame==2.6.1
    + requests==2.32.5
    + shunkei-sdk==0.2.1
    + urllib3==2.5.0
    + zeroconf==0.119.0
   ```

   確認のため以下を実行するとPython3.12となっていることがわかります。

   ```
   PS > uv run python -V
   Python 3.12.12
   ```

   UVでは直接Pythonを実行しても仮想環境が使用されないためご注意ください。

## 実行

`pc` ディレクトリに移動して、Pythonスクリプトを実行します。

```sh
uv run python main.py
```

ターミナル画面と、操作用のウィンドウが起動します。

接続先のShunkei VTX送信機は、mDNSを利用して自動的に検索されます。

別のセグメントにShunkei VTX送信機がある場合など、mDNSで検索できない場合は、
実行時のコマンドライン引数を用いてIPアドレスを指定してください。

```sh
uv run python main.py --host <ip_addr>
```

## G29で運用する場合

### 準備

G29での動作には依存パッケージのインストールが必要になります。

```sh
sudo apt install libhidapi-dev # for linux (Debian系)
brew install hidapi # for mac
```

### 起動方法

G29は自動認識ができないため、ソフトウェア起動時に `--g29` オプションをつけて起動してください。

```sh
python -m pipenv run python main.py --g29
```

## ToDO

- [ ] 接続失敗時のGUIへのエラー表示
- [ ] WebRTCを用いたNAT越え対応

