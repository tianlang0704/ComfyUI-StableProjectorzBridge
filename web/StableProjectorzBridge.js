import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js"

console.log("[StableProjectorzBridge]", "Loading js extension");
const FILENAME_FORMAT_INIT_PREFIX = 'ProjectorInitBlob_{0}_'
const FILENAME_FORMAT_CONTROLNET_PREFIX = 'ProjectorControlnetBlob_{0}_'
const FILENAME_FORMAT_OUTPUT_PREFIX = 'ProjectorOutputBlob_{0}_'
const FILENAME_FORMAT_INIT_PREFIX_DEFAULT = FILENAME_FORMAT_INIT_PREFIX.replace("{0}", "0")
const FILENAME_FORMAT_CONTROLNET_PREFIX_DEFAULT = FILENAME_FORMAT_CONTROLNET_PREFIX.replace("{0}", "0")
const FILENAME_FORMAT_OUTPUT_PREFIX_DEFAULT = FILENAME_FORMAT_OUTPUT_PREFIX.replace("{0}", "0")
const DEFAUL_VALUE_TEXT = "!!!Autofill when executed!!!";
let input_init_prefix = FILENAME_FORMAT_INIT_PREFIX_DEFAULT;
let input_controlnet_prefix = FILENAME_FORMAT_CONTROLNET_PREFIX_DEFAULT;
let output_prefix = FILENAME_FORMAT_OUTPUT_PREFIX_DEFAULT;
let data = {};
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
		}
		else if (nodeType.comfyClass === 'ProjectorzControlnetInput') {
			const this_handler = function() {
				const prefix_widget = this.widgets[1];
				prefix_widget.value = input_controlnet_prefix;
			}
			const onSerialize = nodeType.prototype.onSerialize;
			nodeType.prototype.onSerialize = async function(...args) {
				if(onSerialize) await onSerialize.call(this, ...args);
				this_handler.call(this);
			}
		}
		else if (nodeType.comfyClass === 'ProjectorzOutput') {
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
		else if (nodeType.comfyClass === 'ProjectorzParameter') {
			const this_handler = function() {
				const name = this.widgets[0];
				const value = this.widgets[1];
				if (data[name.value] == undefined) {
					value.value = DEFAUL_VALUE_TEXT;
					return;
				}
				value.value = data[name.value];
			}
			const onSerialize = nodeType.prototype.onSerialize;
			nodeType.prototype.onSerialize = async function(...args) {
				if(onSerialize) await onSerialize.call(this, ...args);
				this_handler.call(this);
			}
		}
		else if (nodeType.comfyClass === 'ProjectorzControlnetParameter') {
			const this_handler = function() {
				const index = this.widgets[0];
				const name = this.widgets[1];
				const value = this.widgets[2];
				const parameter = data.alwayson_scripts?.controlnet?.args?.[index.value]?.[name.value];
				if (parameter == undefined) {
					value.value = DEFAUL_VALUE_TEXT;
					return;
				}
				value.value = parameter;
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
	data = params.json_data ?? "{}";
	input_init_prefix = FILENAME_FORMAT_INIT_PREFIX.replace("{0}", randomId);
	input_controlnet_prefix = FILENAME_FORMAT_CONTROLNET_PREFIX.replace("{0}", randomId);
	output_prefix = FILENAME_FORMAT_OUTPUT_PREFIX.replace("{0}", randomId);
	const n_iter = data.n_iter ?? 1;
	await app.queuePrompt(0, n_iter)
	respond(callId, "done");
}