# meeting 10.12.2025

### Max, Leo, Felix, Anne

## Kick-off

### Why do we want it?

- Vision as a service within DLR for rapid testing w/o vision deployment
- One time implementation and then usage for:
    - EU projects
    - Vision stack for friendly competition (see euROBIN)
- PCVP vision  accessible to the world a Service - make our beautiful research and vision pipeline (e.g Mercedes )

### Outcome

User provides: camera intrinsics + image

We provide: poses (and image with rendered overlay)

### MVP

Accessible PCVP detection pipeline for YCB-V objects with:

- yolov7
- dense pose
- m3t refinement
- result rendering / creation

the access to the pipeline is limited to a certain user group.
Avoids queues, Exportkontrolle and DLR discussions if we do not support public access.

#### MVP Backend

    Internally available call to the PCVP pipeline from within DLR

#### MVP Frontend

    Minimal website where we can upload an image & intrinsics, output pose and image with overlay.

## Next steps

1. Meet and get input from @seth.
   - What are our possibilities for exposing the pipeline to the outside of DLR?
   - How would he approach it?
   - Authentication (user login, support initial **only for one** user at a time)
   - Where and why can we host a website or server that is accessible for outsiders and insiders
   - Combination API call python + website host together
   - Do we need other people or approval from someone?

2. How do we implement it?
   - [FastAPI](https://fastapi.tiangolo.com/)?
   - using the restful guidelines
   - [possible backend: gradio](https://www.gradio.app/), self-hosted or within Github/Gitlab?
