# Simplify — Multimodal Similarity Architecture

Simplify is a multimodal similarity engine designed to analyze, cluster, and organize large collections of files. It extracts modality‑specific embeddings for images, audio, video, and documents, and indexes them in FAISS for fast similarity search.

The system is built around a content‑centric model, where every file produces one or more streams, each stream produces embeddings, and embeddings are indexed in FAISS with a clean mapping back to the originating content.

## 1. Core Concepts

### 1.1 Physical Files

![filesystem structure](<./architecture-media/d1.png>)

Physical files are the raw items found on disk. They may be:

simple files (JPEG, PNG, MP3, WAV, PDF, DOCX)

containers (ZIP, TIFF, MKV, MP4, HEIC)

Each physical file is identified by a file_hash.

### 1.2 Streams

A stream is the decoded content extracted from a file.

- Non‑container file → 1 stream

- Container file → N streams (pages, frames, tracks, attachments)

Each stream is identified by a content_hash.

### 1.3 Embeddings

Each stream produces one or more embeddings depending on modality:

- CLIP, ORB, pHash (images)

- Chromaprint, MFCC, OpenL3 (audio)

- FlowHash, I3D, OpenL3‑Video (video)

- E5‑Large, LayoutLMv3, SigLIP (documents)

### 1.4 FAISS Index

FAISS indexes vectors, not hashes.

Simplify maintains a mapping:

- faiss_id → content_hash

- content_hash → stream

- stream → file_hash

## 2. System Architecture

The architecture is composed of five major subsystems:

1. File Registry

1. Stream Registry

1. Processing Pipelines

1. Modality Engines

1. Embeddings Registry + FAISS Index

## 3. File Registry

The File Registry stores metadata for every physical file discovered by the scanner.

**Fields**:

- `path` (posix normalized, primary key)

- `file_hash` — strong hash of raw bytes

- `file_name`

- `extension`

- `parent_path`

- `size`

- `is_container_type`

- `file_type` (image, audio, video, document, file_container, other)

- timestamps:
  - `OS_creation_date`
  - `OS_last_modified_date`

- metadata (JSON)

### 3.1 Responsibilities

- Deduplication of physical files

- Routing files to correct pipelines

- Tracking container vs. non‑container types

## 4. Stream Registry

Every file produces one or more **streams**.

Streams represent decoded content.

**Fields**:

- `stream_id` — primary key

- `file_hash` — parent file

- `index` — page/frame/track number

- `modality` — image/audio/video/document

- `content_hash` — hash of decoded content

- `metadata` — EXIF, ID3, MKV tags, PDF metadata, etc. (JSON)

### 4.1 Responsibilities

- Deduplicate decoded content

- Link containers to internal streams

- Link streams to modality embeddings

- Provide unified identity for FAISS indexing

## 5. Scanner Pipeline

The scanner discovers files, hashes them, classifies them, and routes them to the correct processing pipeline.

### 5.1 Scan

- Recursively traverse folders

- Identify files and containers

### 5.2 Hash

- Compute `file_hash`

  - If exists → skip processing

  - If new → register in `files`

### 5.3 Classify

- Determine modality or container type

- Route to correct pipeline

### 5.4 Extract

- Non‑container → decode content → produce 1 stream

- Container → decode internal streams → produce N streams

### 5.5 Embed

- Generate modality‑specific embeddings

### 5.6 Index

- Insert embeddings into FAISS

- Map `faiss_id` → `content_hash`

## 6. Container Processing Pipeline

Containers are treated as structured envelopes. Their internal streams are virtually extracted (decoded in memory, not written to disk).

### 6.1 Hash Container

- Compute `file_hash`

  - If exists → skip extraction

### 6.2 Extract Streams

Depending on container type:

- ZIP → internal files

- TIFF → pages/layers

- GIF/WebP → frames

- HEIC → primary + auxiliary images

- MKV/MP4 → video/audio/subtitles/attachments

- MXF → multi‑track professional media

### 6.3 Normalize Streams

- Decode pixels

- Decode PCM audio

- Decode video frames

- Extract metadata

### 6.4 Hash Streams

Compute `content_hash`

Deduplicate across containers

### 6.5 Embed Streams

- Generate modality embeddings

### 6.6 Index Streams

- Insert vectors into FAISS

- Map faiss_id → content_hash

### 6.7 Link Streams

- Record file_hash → stream_id[]

## 7. Non‑Container Processing Pipeline

Non‑container files produce exactly one stream.

**Steps**:

1. Decode content

1. Compute content_hash

1. Insert into streams

1. Generate embeddings

1. Insert embeddings into FAISS

1. Map faiss_id → content_hash

## 8. Modality Engines

### 8.1 Image Similarity

- pHash

- ORB

- CLIP Vision

### 8.2 Audio Similarity

- Chromaprint

- MFCC

- OpenL3

### 8.3 Video Similarity

- pHash + FlowHash

- I3D Flow

- OpenL3‑Video

### 8.4 Document Similarity

- E5‑Large

- LayoutLMv3

- SigLIP

## 9. Embeddings Registry

The Embeddings Registry stores all modality vectors.

There's one Embeddings Registry table per FAISS index

**Fields**:

- `content_hash`

- `modality`

- `embedding_type`

- `vector`

- `FAISS_index_id`

- `metadata`

**Responsibilities**:

- Provide unified lookup for FAISS

- Support multimodal search

- Enable cross‑modal clustering

## 10. FAISS Indexing

FAISS indexes vectors, not hashes.

### 10.1 Correct Model

1. Insert vector → FAISS assigns faiss_id

1. Store mapping:

    - faiss_id → content_hash

1. Use content_hash to retrieve:

    - stream

    - file

    - container

### 10.2 Benefits

- Fast nearest‑neighbor search

- Scalable to millions of vectors

- Supports multimodal clustering

## 11. Deduplication Model

- **Physical Deduplication**
  - Based on file_hash

  - Detects identical files on disk

- **Content Deduplication**
  - Based on content_hash

  - Detects identical decoded content

  - Works across containers

- **Embedding Deduplication**

  - Based on FAISS similarity

  - Detects near‑duplicates

  - Detects semantically similar content

## 12. System Capabilities

- Multimodal duplicate detection

- Similarity‑based clustering

- Intelligent organization

- Cross‑modal search

- Container‑aware processing

- Scalable FAISS indexing

- Metadata‑aware enrichment

## Summary

Simplify is a multimodal similarity engine built on a unified content‑centric architecture. Physical files produce streams, streams produce embeddings, and embeddings are indexed in FAISS with a clean mapping back to content and containers. This design ensures correctness, scalability, and efficient multimodal similarity across images, audio, video, documents, and container formats.
