# Large Language Models (LLMs)

Large Language Models are neural networks trained on massive text data to understand and generate human-like text.

## Transformer Architecture

The transformer architecture, introduced in "Attention Is All You Need" (Vaswani et al., 2017), revolutionized NLP.

### Key Components

- **Attention Mechanism**: Allows the model to focus on relevant parts of the input
- **Multi-Head Attention**: Multiple attention layers in parallel
- **Feed-Forward Networks**: Position-wise transformations
- **Positional Encoding**: Adds position information to token embeddings

### Self-Attention

Self-attention computes attention scores between all pairs of positions in a sequence. For a query Q, key K, and value V:

```
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
```

## Types of LLMs

### Encoder-Only (BERT)
- Bidirectional context
- Best for understanding tasks (classification, NER)
- Examples: BERT, RoBERTa

### Decoder-Only (GPT)
- Autoregressive generation
- Best for text generation
- Examples: GPT-4, Llama, Gemma

### Encoder-Decoder (T5)
- Sequence-to-sequence
- Best for translation, summarization
- Examples: T5, BART

## Prompt Engineering

Prompt engineering is the practice of designing inputs to guide LLM outputs.

Key techniques:
- **Few-shot prompting**: Providing examples in the prompt
- **Chain-of-thought**: Step-by-step reasoning
- **System prompts**: Setting behavior constraints
- **Temperature**: Controls randomness (0 = deterministic, 1 = creative)
- **Top-K sampling**: Limits next token choices to K most likely

## Fine-tuning

Fine-tuning adapts a pre-trained model to a specific task by training on task-specific data. Methods:
- **Full fine-tuning**: Update all parameters (expensive)
- **LoRA**: Low-Rank Adaptation (efficient)
- **QLoRA**: Quantized LoRA (even more efficient)

## Quantization

Quantization reduces model size and inference cost by using lower-precision numbers. Common formats:
- FP16 (half precision)
- INT8 (8-bit integer)
- Q4_K_M (4-bit, used by Ollama default)

## Running LLMs Locally

Local LLM inference tools:
- **Ollama**: Easy-to-use local LLM runner
- **llama.cpp**: C++ inference engine
- **vLLM**: High-performance inference server
- **Hugging Face Transformers**: Python library

Ollama manages model downloads and provides a REST API at localhost:11434 for inference.
