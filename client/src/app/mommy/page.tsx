"use client";

import { useEffect, useState } from "react";
import Markdown from "react-markdown";
import {
	CartesianGrid,
	Line,
	LineChart,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";

interface Props { }
interface ChatObject {
	sender: "user" | "mommy";
	message: string;
}

const page = (props: Props) => {
	const [chatInput, setChatInput] = useState<string>("");
	const [chatHistory, setChatHistory] = useState<ChatObject[]>([]);

	async function sendChat() {
		// fetch data from localhost 5000

		// add the user's chat to the chat history

		let newChatHistory: ChatObject[] = [
			...chatHistory,
			{ sender: "user", message: chatInput },
		];

		setChatHistory(newChatHistory);

		const response = await fetch("http://127.0.0.1:5000/ask", {
			body: JSON.stringify({ history: newChatHistory }),
			headers: {
				"Content-Type": "application/json",
			},
			method: "POST",
		});
		const reader = response.body?.getReader();

		if (!reader) return;

		let done = false;
		let data = "";
		while (!done) {
			const { value, done: done_ } = await reader.read();
			done = done_;
			data += new TextDecoder().decode(value);

			// update the last chat
			// if the last chat object is from the user
			// then add a new chat object with the response from the server
			// else update the last chat object with the response from the server
			setChatHistory((oldChatHistory) => {
				if (oldChatHistory.length > 0) {
					if (oldChatHistory[oldChatHistory.length - 1].sender === "user") {
						return [
							...oldChatHistory.slice(0, -1),
							{ sender: "user", message: chatInput },
							{ sender: "mommy", message: data },
						];
					} else {
						const newChatHistory = oldChatHistory.slice(0, -1);
						return [...newChatHistory, { sender: "mommy", message: data }];
					}
				} else {
					return [{ sender: "mommy", message: data }];
				}
			});
		}
		fetchActions();
	}

	const [data, setData] = useState<any[]>();
	const [biometrics, setBiometrics] = useState<any>();
	useEffect(() => {
		function fetchData() {
			// fetch data from localhost 5000
			fetch("http://127.0.0.1:5000/history")
				.then((res) => res.json())
				.then((data) => {
					console.log(data);
					setData(data.history);
					setBiometrics(data.biometrics);
				});
		}

		// interval to fetch data every 5 seconds
		try {
			fetchData();
		} catch (e) {
			console.log("Error fetching data");
		}

		const interval = setInterval(() => {
			console.log("fetching data...");
			try {
				fetchData();
			} catch (e) {
				console.log("Error fetching data");
			}
		}, 500);

		return () => clearInterval(interval);
	}, [setData]);

	const [actions, setActions] = useState<any[]>();
	function fetchActions() {
		fetch("http://127.0.0.1:5000/rules")
			.then((res) => res.json())
			.then((data) => {
				console.log(data);
				setActions(data);
			});
	}
	useEffect(() => {
		// interval to fetch data every 5 seconds
		try {
			fetchActions();
		} catch (e) {
			console.log("Error fetching actions");
		}
	}, [setActions]);

	return (
		<div className="w-screen min-h-screen flex flex-col items-center bg-pink-50">
			<div className="flex flex-col gap-4 items-center justify-center py-36">
				<img src="/mommy.webp" alt="Mommy" className="w-48 rounded-lg mb-2  " />
				<h1 className="text-4xl font-bold text-black text-center">
					💕 AI MOMMY 💕
				</h1>
				<p className="text-gray-400 text-center italic">
					*softly whispers with a gentle, soothing tone*
					<br />
					"Mmm~ how can I help you, baby?~" 💕 gentle giggle
				</p>

				{chatHistory.length > 0 && (
					<div className="w-[40rem] bg-pink-100 rounded-lg p-4 flex flex-col gap-2 max-h-[80vh] overflow-scroll">
						{chatHistory.map((chat, index) => (
							<div
								key={index}
								className={`flex w-full ${chat.sender === "user" ? "justify-end" : "justify-start"
									}`}
							>
								<div
									className={`p-2 overflow-hidden ${chat.sender === "user" ? "bg-pink-200" : "bg-pink-300"
										} rounded-lg max-w-[75%]`}
								>
									<div className="text-black">
										<Markdown>{chat.message}</Markdown>
									</div>
								</div>
							</div>
						))}
					</div>
				)}

				<div className="w-[40rem] bg-pink-100 rounded-lg p-4">
					<input
						type="text"
						value={chatInput}
						onChange={(e) => setChatInput(e.target.value)}
						onKeyDown={(e) => {
							if (e.key === "Enter") {
								sendChat();
								setChatInput("");

								// setChatHistory([
								// 	...chatHistory,
								// 	{ sender: "user", message: chatInput },
								// ]);
							}
						}}
						className="w-full bg-transparent outline-none text-black"
						placeholder="type something babyyy..."
					></input>
				</div>
			</div>

			<div className="w-full flex flex-col items-center gap-8 pb-20">
				{actions &&
					actions.map((action: any, index) => (
						<Action action={action} data={data} biometrics={biometrics} key={index} />
					))}
			</div>
		</div>
	);
};

function Action({ action, data, biometrics }: { action: any; data?: any[]; biometrics?: any }) {
	return (
		<div className="flex w-[50rem] bg-pink-100 rounded-lg p-4 gap-4">
			<div className="flex flex-1 flex-col gap-4">
				<p className="font-semibold italic text-black">
					{action.condition_cute}
				</p>
				<ul className="text-gray-700 space-y-1">
					{action.actions_cute.map((action: string, index: number) => (
						<li key={index} className="list-none">
							{action}
						</li>
					))}
				</ul>
				<p className="font-semibold italic text-black">
					{action.priority_cute}
				</p>
			</div>
			<div className="w-40 h-64 bg-white rounded-lg flex items-center justify-center flex-1 flex-col gap-2 text-black">
				{data && (
					<ResponsiveContainer width="100%" height="100%">
						<LineChart
							data={data}
							margin={{ top: 15, right: 15, left: 15, bottom: 5 }}
						>
							<XAxis dataKey="name" stroke="#8884d8" />
							<YAxis
								yAxisId={1}
								stroke="#8884d8"
								// label={"ur stress 🥺"}
								mirror={true}
								domain={[0, 500]}
								max={500}
							/>
							<Tooltip
								contentStyle={{
									backgroundColor: "#fff",
									borderRadius: "8px",
									border: "none",
									boxShadow: "0px 0px 10px rgba(0, 0, 0, 0.1)",
								}}
							/>
							<CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
							<Line
								animationDuration={0}
								type="monotone"
								dataKey="stress"
								stroke="#f472b6"
								strokeWidth={3}
								yAxisId={1}
								dot={false}
								// dot={{ r: 5, strokeWidth: 2, fill: "#f472b6" }}
								activeDot={{ r: 8 }}
							/>
						</LineChart>
					</ResponsiveContainer>
				)}
				{biometrics && (
					<div className="flex gap-2">
						<Number number={`💓 ${Math.round(biometrics?.heart_rate)}`} />
						<Number number={`🩸 ${Math.round(biometrics?.blood_pressure_high)} / ${Math.round(biometrics?.blood_pressure_low)}`} />
						<Number number={`🌡️ ${Math.round(biometrics?.body_temperature)}`} />
					</div>
				)}
			</div>
			
		</div>
	);
}

function Number({ number }: { number: any }) {
	return (
		<div className="flex gap-2 bg-pink-200 rounded-lg p-2">
			<p className="text-gray-700">{number}</p>
		</div>
	);
}

export default page;
