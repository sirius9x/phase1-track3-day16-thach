import json
import random
from pathlib import Path

def prepare_data():
    input_path = Path(r"C:\Users\sirius\OneDrive\Desktop\hotpot_dev_distractor_v1.json\hotpot_dev_distractor_v1.json")
    output_path = Path(r"data\hotpot_test.json")
    
    print(f"Loading {input_path}...")
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"Total records in HotpotQA: {len(data)}")
    
    # Pick 105 random records
    random.seed(42)
    sample = random.sample(data, 105)
    
    converted = []
    for item in sample:
        context_chunks = []
        for title, sentences in item["context"]:
            context_chunks.append({
                "title": title,
                "text": " ".join(sentences)
            })
            
        converted.append({
            "qid": item["_id"],
            "difficulty": item.get("level", "medium"),
            "question": item["question"],
            "gold_answer": item["answer"],
            "context": context_chunks
        })
        
    print(f"Saving {len(converted)} records to {output_path}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(converted, f, indent=2, ensure_ascii=False)
        
    print("Done!")

if __name__ == "__main__":
    prepare_data()
