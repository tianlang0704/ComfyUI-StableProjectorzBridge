import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js"

console.log("[StableProjectorzBridge]", "Loading js extension");
const FILENAME_FORMAT_INIT_PREFIX = 'ProjectorInitBlob_{0}_'
const FILENAME_FORMAT_CONTROLNET_PREFIX = 'ProjectorControlnetBlob_{0}_'
const FILENAME_FORMAT_OUTPUT_PREFIX = 'ProjectorOutputBlob_{0}_'
const FILENAME_FORMAT_INIT_PREFIX_DEFAULT = FILENAME_FORMAT_INIT_PREFIX.replace("{0}", "0")
const FILENAME_FORMAT_CONTROLNET_PREFIX_DEFAULT = FILENAME_FORMAT_CONTROLNET_PREFIX.replace("{0}", "0")
const FILENAME_FORMAT_OUTPUT_PREFIX_DEFAULT = FILENAME_FORMAT_OUTPUT_PREFIX.replace("{0}", "0")
let input_init_prefix = FILENAME_FORMAT_INIT_PREFIX_DEFAULT;
let input_controlnet_prefix = FILENAME_FORMAT_CONTROLNET_PREFIX_DEFAULT;
let output_prefix = FILENAME_FORMAT_OUTPUT_PREFIX_DEFAULT;
let socket;
app.registerExtension({
	name: "Comfy.StableProjectorzBridge",
	init() {
	},
	async setup() {
		setInterval(() => {
			if (!socket) {
				createSocket();
			}
		}, 1000);
	},
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		if (nodeType.comfyClass === 'ProjectorzInitInput') {
			const this_handler = function() {
				const prefix_widget = this.widgets[1];
				prefix_widget.value = input_init_prefix;
			}
			const onSerialize = nodeType.prototype.onSerialize;
			nodeType.prototype.onSerialize = async function(...args) {
				if(onSerialize) await onSerialize.call(this, ...args);
				this_handler.call(this);
			}
		}else if (nodeType.comfyClass === 'ProjectorzControlnetInput') {
			const this_handler = function() {
				const prefix_widget = this.widgets[1];
				prefix_widget.value = input_controlnet_prefix;
			}
			const onSerialize = nodeType.prototype.onSerialize;
			nodeType.prototype.onSerialize = async function(...args) {
				if(onSerialize) await onSerialize.call(this, ...args);
				this_handler.call(this);
			}
		}else if (nodeType.comfyClass === 'ProjectorzOutput') {
			const this_handler = function() {
				const prefix_widget = this.widgets[0];
				prefix_widget.value = output_prefix;
			}
			const onSerialize = nodeType.prototype.onSerialize;
			nodeType.prototype.onSerialize = async function(...args) {
				if(onSerialize) await onSerialize.call(this, ...args);
				this_handler.call(this);
			}
		}
	}
});

function createSocket(){
	socket = new WebSocket(
		`ws${window.location.protocol === "https:" ? "s" : ""}://${api.api_host}/A1111/v1/init_client`
	);
	socket.addEventListener("open", () => {
	});
	socket.addEventListener("error", () => {
		if (socket) socket.close();
	});
	socket.addEventListener("close", () => {
		setTimeout(() => {
			socket = null;
		}, 300);
	});
	socket.addEventListener("message", (event) => {
		try {
			const msg = JSON.parse(event.data);
			switch (msg.action) {
				case "run_prompt":
					run_prompt(msg.call_id, msg.params);
					break;
				default:
					console.warn("Unhandled message:", event.data);
					break;
			}
		} catch (error) {
			console.warn("Unhandled message:", event.data, error);
		}
	});
}

async function respond(callId, result) {
	socket.send(JSON.stringify({
		call_id: callId,
		result: result,
	}));
}

async function run_prompt(callId, params) {
	const randomId = params.random_id ?? "0";
	const batch = params.batch ?? 1;
	input_init_prefix = FILENAME_FORMAT_INIT_PREFIX.replace("{0}", randomId);
	input_controlnet_prefix = FILENAME_FORMAT_CONTROLNET_PREFIX.replace("{0}", randomId);
	output_prefix = FILENAME_FORMAT_OUTPUT_PREFIX.replace("{0}", randomId);
	await app.queuePrompt(0, batch)
	respond(callId, "done");
}