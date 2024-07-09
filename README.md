# Install
The best easiest way is to use ComfyUI Manager to install.

# Use
1. Create a workflow with Projector Controlnet Input as input, and Projectorz Output as output
2. Click Gen Art in Stable Projectorz
3. Done

# Info
This custom nodes enables Stable Projectorz to work with ComfyUI Directly.

StableProjectorz sends only controlnet images/masks and inpaint images/masks to ComfyUI nodes, and then ComfyUI process them and sends them back to StableProjectorz.

All settings in Stable Projectorz are accessable through ProjectorzParameter node and ProjectorzControlnetParameter node.

Enjoy!

<br />
<a href="samples/ProjectorzGen_Sample.json">Sample workflow for Generating with Controlnet(the default way with Projectorz)</a>
<br />
<img width="250" src="./samples/ProjectorzGen_Sample.png">
<br />
<a href="samples/ProjectorzInpaint_Sample.json">Sample workflow for inpainting(Projectorz brush fill)</a>
<br />
<img width="250" src="./samples/ProjectorzInpaint_Sample.png">
<br />
Basic settings:
<br />
<img width="241" src="https://github.com/tianlang0704/ComfyUI-StableProjectorzBridge/assets/12490479/539f44ed-78ef-46fb-a262-e5a314ed439f">
<br />
<img width="422" src="https://github.com/tianlang0704/ComfyUI-StableProjectorzBridge/assets/12490479/b3efe776-fb26-4f4f-959b-0c13e2e3418d">
<br />
<img width="427" src="https://github.com/tianlang0704/ComfyUI-StableProjectorzBridge/assets/12490479/0dfccf2a-290e-43c4-8014-23b2fc1e5c55">
<br />
<img width="931" src="https://github.com/tianlang0704/ComfyUI-StableProjectorzBridge/assets/12490479/b5a92132-8538-481b-909c-ca4709f300b0">
<br />
<img width="600" src="https://github.com/tianlang0704/ComfyUI-StableProjectorzBridge/assets/12490479/05db7d2a-615b-479b-bf3b-243f6d43df92">
