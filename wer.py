from jiwer import wer

ref = "hello everyone welcome to the meeting"
hyp = "hello everyone welcome meeting"

print("WER:", wer(ref, hyp))