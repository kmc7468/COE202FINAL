# 2023F CoE202 Final Project
## 프로젝트 구조
- **Client:** 마이크가 설치된 Device입니다. 사용자의 음성을 인식, 분석한 뒤, 로봇이 수행해야 할 명령을 Server로 전송합니다.
- **Server:** MODI와 연결된 Device입니다. 주변 환경을 인식하고, 사용자의 명령을 수행합니다.

## 초기 설정 방법
```
git clone https://github.com/kmc7468/COE202FINAL.git
cd COE202FINAL
cd Client
pip install dotenv openai
cd ../Server
pip install dotenv
cd ..
```
최초 1회만 하면 됩니다.

## 실행 방법
- Client: `python client`
- Server: `python server`

## git 사용 방법
### 변경사항 서버로 업로드
```
git add --all
git commit -m "메시지"
git push
```
메시지는 아무 값이어도 상관이 없으나, 본인이 작업한 결과물에 대한 설명이면 좋습니다.

### 변경사항 서버에서 다운로드
```
git pull
```

## 역할 분담
- **승윤:** Image processing
- **민찬:** Voice recognition
- **민성:** Motor motion (Embedded programming MODI) 