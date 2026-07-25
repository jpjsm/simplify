# Simplify — Multimodal Similarity Architecture

## Overview

![Simplify Architecture](<./Simplify-content_design.png>)
Simplify is a multimodal similarity engine designed to analyze, cluster, and organize large collections of files. It extracts specialized similarity vectors for each content type—images, audio, video, and documents—and indexes them in FAISS for efficient nearest‑neighbor search.

The system is built around a **content‑centric architecture**, where each file is uniquely identified by its content hash and enriched with modality‑specific embeddings.

---

## 1. File Registry (`files`)

The `files` table is the root of the system.

**Fields**

- `path` — primary key  
- `hash` — content uniqueness  
- metadata fields (size, extension, timestamps, etc.)

**Capabilities**

- duplicate detection  
- type statistics  
- extension distribution analysis  

---

## 2. Image Similarity (`image_similarity`)

Simplify computes three complementary visual descriptors:

- **pHash** — perceptual hashing for near‑duplicate detection  
- **ORB** — keypoint‑based structural similarity  
- **CLIP Vision** — semantic visual embeddings  

These vectors allow Simplify to detect exact duplicates, near‑duplicates, and semantically related images.

---

## 3. Audio Similarity (`audio_similarity`)

Audio files are analyzed using:

- **Chromaprint** — robust audio fingerprinting  
- **MFCC** — timbre and spectral characteristics  
- **OpenL3** — deep multimodal audio embeddings  

This combination supports duplicate detection, similarity clustering, and perceptual matching.

---

## 4. Video Similarity (`video_similarity`)

Video similarity integrates structural, motion, and audio‑visual embeddings:

- **pHash + FlowHash** — frame and motion hashing  
- **I3D Flow** — deep action/motion representation  
- **OpenL3‑Video** — multimodal audiovisual embeddings  

This enables detection of visually similar clips, near‑duplicates, and related content.

---

## 5. Document Similarity (`doc_similarity`)

Document similarity is multimodal and integrates text, structure, vision, and metadata.

### 5.1 Text Embedding

Simplify uses **E5‑Large** for semantic text similarity.

- High‑quality embeddings  
- Excellent for clustering and retrieval  
- Robust for long documents  

### 5.2 Layout Embedding

Structural document features are extracted using **LayoutLMv3**.

- Captures spatial relationships  
- Ideal for PDFs with tables, forms, diagrams  
- Complements text embeddings  

### 5.3 Vision Embedding

Document pages are treated as images and encoded with **SigLIP**.

- Stable visual embeddings  
- Strong clustering performance  
- Useful for scanned documents  

### 5.4 Metadata Features

Simplify incorporates lightweight metadata signals:

- PDF metadata (title, author, creation date)  
- keyphrases extracted from text  
- structural indicators (page count, file size)

Metadata improves clustering accuracy and reduces unnecessary embedding computation.

---

## 6. FAISS Indexing

All similarity vectors are indexed in FAISS using the file’s content hash as the unique identifier.

FAISS enables:

- nearest‑neighbor search  
- multimodal clustering  
- duplicate and near‑duplicate detection  
- scalable similarity queries across millions of files  

---

## 7. System Capabilities

Simplify supports:

- multimodal duplicate detection  
- similarity‑based clustering  
- intelligent organization of large file collections  
- cross‑modal search (image ↔ document ↔ video)  
- scalable indexing and retrieval  

---

## Summary

The architecture integrates modality‑specific similarity mechanisms with a unified FAISS backend.  
Each file is represented by its content hash and enriched with multimodal embeddings, enabling fast, scalable, and accurate similarity search across diverse file types.
