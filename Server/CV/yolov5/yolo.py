import threading
import detect

def func():
	detect.run(source=0)

thread = threading.Thread(target=func, daemon=True)

thread.start()

def get():
	return detect.objects[-1]

input()
print(get())


    
