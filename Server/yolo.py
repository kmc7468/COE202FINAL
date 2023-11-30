import CV.yolov5.detect as detect

def func():
	detect.run()

thread = threading.Thread(target=func, daemon=True)

def get():
	return detect.objects