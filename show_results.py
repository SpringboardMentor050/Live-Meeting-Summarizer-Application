import os

def display():
    base = r"f:/LiveMeetingAnalyzerProject"
    t_path = os.path.join(base, "MILESTONE2_DELIVERABLE_diarized_transcript.txt")
    s_path = os.path.join(base, "MILESTONE2_DELIVERABLE_summary.md")

    print("\n" + "="*80)
    print(" MILESTONE 2: SPEAKER DIARIZATION & SUMMARIZATION ENGINE ")
    print("="*80)

    if os.path.exists(t_path):
        print("\n[PART 1: DIARIZED TRANSCRIPT SNIPPET]")
        with open(t_path, "r", encoding="utf-8") as f:
            print(f.read()[:800] + "...") # Show first 800 chars
    else:
        # Check for previous result names
        t_fallback = os.path.join(base, "YOUTUBE_FINAL_REPORT_diarized_transcript.txt")
        if os.path.exists(t_fallback):
             with open(t_fallback, "r", encoding="utf-8") as f:
                print(f.read()[:800] + "...") 

    if os.path.exists(s_path):
        print("\n\n" + "="*80)
        print("[PART 2: AI-GENERATED EXECUTIVE SUMMARY]")
        print("="*80 + "\n")
        with open(s_path, "r", encoding="utf-8") as f:
            print(f.read())
        print("\n" + "="*80)
    else:
        s_fallback = os.path.join(base, "YOUTUBE_FINAL_REPORT_summary.md")
        if os.path.exists(s_fallback):
             with open(s_fallback, "r", encoding="utf-8") as f:
                print(f.read())

if __name__ == "__main__":
    display()
