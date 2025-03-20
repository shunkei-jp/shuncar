# Shuncar 操縦用PC用プログラム

## 対応コントローラー一覧

以下のコントローラーで動作を確認しています。
これらのコントローラを接続すると、自動で認識してキー配列を設定します。

- SHANWAN JC-U4013S DirectInput Mode ([amazon](https://www.amazon.co.jp/dp/B01N1S3YJP/))
- HORI Racing Wheel Apex ([amazon](https://www.amazon.co.jp/dp/B09P9S5JJ1/))

以下のキーボードに関しては、特殊な操作を行う必要があります。

- Logicool G G29 Driving Force ([amazon](https://www.amazon.co.jp/dp/B00ZQNBTJW/))

## 環境構築

1. Pythonのインストール
   - Python3.11, 3.12 で動作確認がとれています。
2. Pipenvのインストール
   - ```sh
     pip install pipenv
     ```
3. hidapiのインストール (mac / linuxの場合)
   - ```sh
     brew install hidapi # mac
     sudo apt install libhidapi-dev # Debian系
     ```
5. 依存ライブラリのインストール
   - `pc` ディレクトリに移動し、Pipenvを用いて依存ライブラリのインストールを行います。
     ```sh
     python -m pipenv sync

## 実行

`pc` ディレクトリに移動して、Pythonスクリプトを実行します。

```sh
python -m pipenv run python main.py
```

ターミナル画面と、操作用のウィンドウが起動します。

接続先のShunkei VTX送信機は、mDNSを利用して自動的に検索されます。

別のセグメントにShunkei VTX送信機がある場合など、mDNSで検索できない場合は、
実行時のコマンドライン引数を用いてIPアドレスを指定してください。

```sh
python -m pipenv run python main.py --host <ip_addr>
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

