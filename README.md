# NilSagar — AI-Powered Marine Debris & Anomaly Detection System (Side-Scan Sonar)

**Smart India Hackathon 2026 — Problem Statement 26057**
Ministry of Earth Sciences (MoES) / National Institute of Ocean Technology (NIOT)
Category: Software · Theme: Disaster Management

## Overview

NilSagar reads side-scan sonar (SSS) imagery and flags man-made marine debris — with two branches working together: a **supervised classifier** for debris types we have labeled examples of, and a **designed anomaly-detection branch** for debris types no public dataset labels at all. This repo currently ships the supervised branch as a working, tested model; the anomaly branch and raw-sonar preprocessing stage are fully designed and documented below, pending real field data.

## Why this approach

India does not currently have a public, labeled side-scan sonar debris dataset. Every dataset used here (KLSG, Marine-PULSE, AI4Shipwrecks, Seafloor Sediments) was collected and pre-processed by international research groups — meaning the raw acoustic pings were already corrected, cropped, and published as clean images before we ever received them. Our pipeline is designed end-to-end for raw AUV data, but only the stages that operate on the pixel data we actually have were run in this build. That distinction is documented explicitly per stage below, not glossed over.

## Pipeline
```mermaid
flowchart TD
    A["Raw SSS Acoustic Pings<br/><i>(AUV / Towfish)</i>"] --> B

    subgraph PREPROCESSING["<b>PREPROCESSING</b>"]
        direction TB
        B1["Slant-range correction + water-column removal<br/><i>[designed — needs raw pings]</i>"]
        B2["Time-Varying Gain (TVG) normalization<br/><i>[designed — needs raw pings]</i>"]
        B3["Speckle noise reduction (Non-Local Means)<br/><i>[implemented]</i>"]
        B4["Ping-to-mosaic stitching (AUV nav: INS/USBL)<br/><i>[designed — needs raw pings]</i>"]
        B5["CLAHE contrast enhancement<br/><i>[implemented]</i>"]
        B1 --> B2 --> B3 --> B4 --> B5
    end

    B5 --> C

    subgraph TILING["<b>TILING + AUGMENTATION</b> <i>[implemented]</i>"]
        C1["512×512 patch tiling"]
        C2["Rotation, flip, contrast jitter augmentation"]
        C1 --> C2
    end

    C2 --> D1
    C2 --> D2

    subgraph D1["<b>3A. SUPERVISED BRANCH</b> <i>[implemented]</i>"]
        D1a["YOLOv8 classifier, 5 classes<br/>trained on KLSG + Marine-PULSE<br/><b>→ 96.4% test accuracy, MCC 0.948</b><br/><i>(5-fold cross-validation)</i>"]
    end

    subgraph D2["<b>3B. ANOMALY BRANCH</b> <i>[designed]</i>"]
        D2a["Convolutional autoencoder<br/>trained ONLY on normal seabed<br/><i>(Seafloor Sediments dataset)</i><br/><b>→ Flags high reconstruction-error patches</b>"]
    end

    D1a --> E
    D2a --> E

    subgraph FUSION["<b>FUSION & SCORING</b> <i>[designed]</i>"]
        E1["• High detector confidence → labeled debris class"]
        E2["• High anomaly score, low confidence → 'unidentified anomaly, flag for expert review'"]
        E3["• Closes the gap between known debris classes and genuinely novel targets"]
    end

    FUSION --> F["<b>GEOREFERENCING + POST-PROCESSING</b><br/><i>[designed — see note below]</i>"]
    F --> G["<b>DASHBOARD</b><br/><i>[implemented — prototype]</i>"]
    G --> H["<b>HUMAN-IN-THE-LOOP FEEDBACK / ACTIVE LEARNING</b><br/><i>[designed]</i>"]

    %% Styling
    style A fill:#1f2937,stroke:#374151,color:#fff
    style PREPROCESSING fill:#111827,stroke:#3b82f6,color:#fff
    style TILING fill:#111827,stroke:#10b981,color:#fff
    style D1 fill:#064e3b,stroke:#10b981,color:#fff
    style D2 fill:#701a75,stroke:#f43f5e,color:#fff
    style FUSION fill:#1e1b4b,stroke:#6366f1,color:#fff
    style F fill:#1f2937,stroke:#374151,color:#fff
    style G fill:#1f2937,stroke:#10b981,color:#fff
    style H fill:#1f2937,stroke:#374151,color:#fffd)

## Dataset

| Dataset | Used for | Images | Source |
|---|---|---|---|
| SeabedObjects-KLSG | ship, airplane | 370 | github.com/huoguanying/SeabedObjects-Ship-and-Airplane-dataset |
| Marine-PULSE | pipeline/cable, engineering platform, seabed surface | 570 | Zenodo, record 7922705 |
| AI4Shipwrecks | held out — generalization demo only, not trained on | 286 | Univ. of Michigan, DOI 10.7302/dmf4-x492 |
| Seafloor Sediments Dataset | planned for anomaly branch | 434,000+ (52GB) | Univ. of Girona, Zenodo 10209445 — deferred, too large for this build cycle |

**Cleaning applied before training:**
- Removed all "underwater residual mound" images from Marine-PULSE — a natural seabed formation, not debris, and including it would have taught the model to false-flag a harmless geological feature.
- Filtered out any drowning-victim / human-remains images as a safety precaution, regardless of whether the source dataset was expected to contain them.

**Final class set (940 images, 5 classes):** ship (385), pipeline_or_cable (323), seabed_surface (88), engineering_platform (82), airplane (62).

## Results — 5-fold stratified cross-validation

| Fold | Train Acc | Test Acc | Test MCC |
|---|---|---|---|
| 0 | 1.000 | 0.963 | 0.946 |
| 1 | 0.989 | 0.931 | 0.901 |
| 2 | 0.999 | 0.973 | 0.962 |
| 3 | 0.999 | 0.963 | 0.947 |
| 4 | 0.995 | 0.989 | 0.985 |

**Mean test accuracy: 0.964 ± 0.019**
**Mean test MCC: 0.948 ± 0.027**

**Why we report MCC, not just accuracy:** the class distribution above is imbalanced (385 ship images vs. 62 airplane images) — a model that mostly guesses the majority class can still post a deceptively high plain accuracy. MCC uses all four cells of the confusion matrix (true/false positives and negatives) and stays low if a model is secretly just exploiting class imbalance. Ours stayed high (0.948) across every fold, which is the actual evidence that the model is learning real class-distinguishing features, not just guessing "ship" most of the time.

## Why there is no ghost-net class

This is a known, field-wide gap, not something specific to us: real, labeled side-scan sonar images of ghost nets are extremely scarce, because nets are thin, low-acoustic-reflectivity, and easily confused with clutter or fishing-line noise even by expert annotators. The one existing public attempt we found (DRISHTI, built for this same problem statement) trains its ghost-net class entirely on **synthetic** data — nets that were never actually recorded by a real sonar. We chose not to adopt that approach: a classifier trained on synthetic acoustic signatures may not transfer reliably to how a real net actually reflects sound underwater, and shipping that as a "working" class risked giving false confidence in front of judges. Our anomaly branch is designed specifically to route around this gap — nets can be caught as an unlabeled anomaly instead of requiring a labeled class we do not have real data for. We are treating this as a placeholder pending an authoritative Indian-government-released ghost-net dataset, not a solved problem.

## Georeferencing and sonar range — why this stage isn't demoed yet

Georeferencing means converting a detection's pixel position in a sonar image into a real GPS coordinate — done by combining the exact time a ping was fired with the AUV's navigation log (from an inertial navigation system / USBL) at that same moment. This requires the raw survey's navigation data, which the public benchmark datasets used here do not include (they are pre-cropped labeled images with no accompanying nav log), so this stage is designed but not runnable on our current data.

For context on the physical constraints this stage works within: side-scan sonar range and resolution trade off against each other based on the acoustic frequency used. Lower frequencies (around 100 kHz) can reach roughly 300–600 m to each side of the towfish/AUV but produce coarser images; higher frequencies (around 500 kHz) resolve much finer detail but only out to roughly 50–100 m per side. A real deployment has to pick a frequency (or use a dual-frequency system) based on whether the priority is wide-area coverage or fine debris detail — this trade-off is a design constraint for any future AUV survey NilSagar is deployed on, not something the software layer controls.

## A precaution worth documenting: biodegradable material vs. debris

Natural organic matter on the seabed — driftwood, dead fish, decaying kelp — can register as an "anomaly" to our anomaly branch just as readily as plastic or metal debris, since both simply deviate from the model's learned "normal seabed" texture. Flagging biodegradable material as debris isn't just a false positive — it risks sending real cleanup resources after something that would have broken down naturally, and eroding trust in the system's flags. The intended mitigation, not yet implemented, is a persistence check: re-surveying a flagged anomaly over repeat passes. Biodegradable material visibly degrades or disappears over weeks; plastic, metal, and rope do not. This is a planned filter, explicitly called out here rather than silently assumed away.

## Dashboard

A working prototype dashboard is included in this repo (`dashboard.html`).

## Team Members

- SNEHA SUKLABAIDYA
- DEBOJIT NATH
- BIDISHA GOSWAMI
- VED BHANDARY
- ROSHAN UPADHAYA
- MAHATMA DOLEY
