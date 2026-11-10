from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "KarmaCST/nllb-200-distilled-600M-en-to-dz"

print("Loading KarmaCST Dzongkha model...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    src_lang="eng_Latn"
)

model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME
)

def translate_to_dzongkha(text):

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    translated_tokens = model.generate(
        **inputs,
        forced_bos_token_id=tokenizer.convert_tokens_to_ids("dzo_Tibt"),
        max_length=256,
        num_beams=4
    )

    translation = tokenizer.batch_decode(
        translated_tokens,
        skip_special_tokens=True
    )

    return translation[0]


print("\nModel loaded successfully!")

while True:

    english_text = input("\nEnter English text (type exit to quit): ")

    if english_text.lower() == "exit":
        break

    result = translate_to_dzongkha(english_text)

    print("\nDzongkha translation:")
    print(result)