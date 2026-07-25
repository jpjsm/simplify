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

# 8. Container Architecture

Container formats—archives, image containers, audio/video containers, and multimedia bundles—are treated as **content envelopes** rather than atomic files. Simplify extracts, normalizes, and indexes the *internal streams* of these containers while maintaining a lightweight registry for the container itself. This ensures that multimodal similarity is computed on the actual content (images, audio, video, documents), not on the container’s packaging.

---

## 8.1 Overview

Containers are processed using a two‑stage strategy:

1. **Container‑level hashing**  
   Detects bit‑identical containers and avoids redundant extraction.

2. **Stream‑level extraction and indexing**  
   Each internal stream becomes a first‑class item with its own content hash and embeddings.

This preserves correctness even when containers differ in metadata but contain identical content.

---

## 8.2 Container Registry (`containers`)

The `containers` table stores metadata about container files.

**Fields**

- `container_hash` — strong hash of the container’s raw bytes  
- `path` — file location  
- `type` — zip, rar, tar, iso, tiff, mkv, mp4, etc.  
- `metadata` — container‑specific fields (JSON)

**Capabilities**

- Detect bit‑identical containers  
- Skip redundant extraction  
- Track container → stream relationships  
- Support multi‑stream formats (TIFF, MKV, HEIF, MXF)

---

## 8.3 Stream Registry (`streams`)

Each internal item extracted from a container is represented as a **stream**.

**Fields**

- `stream_id` — primary key  
- `container_hash` — parent container  
- `index` — page/frame/track number  
- `modality` — image, audio, video, document  
- `content_hash` — hash of the extracted stream  
- `metadata` — EXIF, ID3, MKV tags, PDF metadata, etc.

**Capabilities**

- Deduplicate streams across containers  
- Reuse embeddings for identical streams  
- Support multimodal similarity  
- Enable cross‑container clustering

---

## 8.4 Processing Pipeline for Containers

### 1. **Hash**

Compute a strong container hash (SHA‑256 or BLAKE3).

- If the container hash already exists → **skip extraction**
- If not → proceed to extraction

### 2. **Extract**

Extract internal streams depending on container type:

- Archives → files  
- TIFF → pages/layers  
- GIF/WebP → frames  
- HEIF/HEIC → primary + auxiliary images  
- MKV/MP4 → video streams, audio tracks, subtitles, attachments  
- MXF → multi‑track professional media

### 3. **Normalize**

Normalize each stream:

- Decode image frames  
- Decode audio PCM or AAC/ALAC  
- Decode video frames or keyframes  
- Extract metadata (EXIF, XMP, ID3, MKV tags)

### 4. **Hash Streams**

Compute `content_hash` for each extracted stream.

- Deduplicate streams across containers  
- Reuse existing embeddings when possible

### 5. **Embed**

Generate modality‑specific embeddings:

- Images → pHash, ORB, CLIP  
- Audio → Chromaprint, MFCC, OpenL3  
- Video → pHash+FlowHash, I3D Flow, OpenL3‑Video  
- Documents → E5‑Large, LayoutLMv3, SigLIP

### 6. **Index**

Store embeddings in FAISS using `content_hash` as the unique identifier.

### 7. **Link**

Record container → stream relationships in the database.

---

## 8.5 Supported Container Types

### Archive Containers

- ZIP, RAR, TAR, ISO  
- Treated as directories  
- Internal files processed individually  
- Container hash used for fast deduplication

### Image Containers

- TIFF (multi‑page, multi‑layer)  
- GIF (animated)  
- WebP (static + animated)  
- HEIF/HEIC (primary + auxiliary images)

### Audio Containers

- M4A/M4B (AAC/ALAC + chapters)  
- MKA (multiple audio tracks)  
- CAF (PCM/AAC/ALAC)

### Video Containers

- MKV (video, audio, subtitles, attachments)  
- MP4 (video, audio, cover art)  
- MXF (professional multi‑track media)

---

## 8.6 Deduplication Strategy

Simplify distinguishes between:

### **Bit‑identical containers**

- Container hashes match  
- Extraction skipped  
- Streams reused

### **Logically identical containers**

- Container hashes differ  
- Internal streams extracted  
- Stream hashes match  
- Embeddings reused  
- FAISS entries reused  
- Containers linked to the same stream IDs

This ensures correctness even when containers differ in compression, ordering, timestamps, or metadata.

---

## 8.7 Benefits

- **Zero redundant work**  
  Streams are embedded once, even if they appear in multiple containers.

- **Perfect multimodal indexing**  
  Every stream receives modality‑specific embeddings.

- **Scalable to millions of files**  
  Container hashing prevents unnecessary extraction.

- **Cross‑container similarity**  
  Identical streams cluster together regardless of packaging.

- **Metadata‑aware organization**  
  Container metadata improves search and classification.

---

## 8.8 Summary

Container formats are treated as structured envelopes containing multimodal streams. Simplify hashes containers for fast deduplication, extracts internal streams for content‑centric processing, and indexes all streams in FAISS using modality‑specific embeddings. This architecture ensures correctness, scalability, and efficient multimodal similarity across archives, image containers, audio/video containers, and professional media formats.

---

## Summary

The architecture integrates modality‑specific similarity mechanisms with a unified FAISS backend.  
Each file is represented by its content hash and enriched with multimodal embeddings, enabling fast, scalable, and accurate similarity search across diverse file types.
