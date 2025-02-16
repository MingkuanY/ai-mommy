"use client";

import { useClientRect } from "@/lib/useClientRect";
import useMousePosition from "@/lib/useMousePosition";
import useWindowDimensions from "@/lib/useWindowDimensions";
import { useEffect, useRef, useState } from "react";
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

interface Props {}
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
		<div className="w-screen min-h-screen flex flex-col items-center bg-slate-50 gap-4">
			<div className="flex flex-col gap-4 items-center justify-center py-36">
				{/* <img
					src="/aimom_trans.webp"
					alt="Mommy"
					className="w-48 rounded-lg mb-2  "
				/> */}
				<div className="mb-2">
					<MotherAvatar />
				</div>
				<h1 className="text-4xl font-bold text-slate-700 text-center">
					🤍 ai mama 🤍
				</h1>
				<p className="text-gray-400 text-center italic">
					Don't worry, mommy's here.
				</p>

				{chatHistory.length > 0 && (
					<div className="w-[40rem] bg-slate-100 rounded-lg p-4 flex flex-col gap-2 max-h-[80vh] overflow-scroll">
						{chatHistory.map((chat, index) => (
							<div
								key={index}
								className={`flex w-full ${
									chat.sender === "user" ? "justify-end" : "justify-start"
								}`}
							>
								<div
									className={`p-2 overflow-hidden ${
										chat.sender === "user" ? "bg-slate-200" : "bg-slate-200"
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

				<div className="w-[40rem] bg-slate-100 rounded-lg p-4">
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
						placeholder="What's up sweetheart?"
					></input>
				</div>
			</div>

			<p className="text-gray-400 text-center italic">
				I know how you're feeling.
			</p>

			<div className="w-[50rem] bg-slate-100 rounded-lg p-4 flex flex-col gap-4">
				<div className="flex flex-row gap-4">
					<p className=" text-slate-700 flex-1 text-center italic ">
						Don't be stressed, sweetie!
					</p>
					<p className=" text-slate-700 flex-1 text-center italic ">
						You make my heart beat 🥰
					</p>
				</div>
				<div className="w-full flex flex-row gap-4">
					<div className="w-40 h-64 bg-white rounded-lg flex items-center justify-center flex-1 flex-col gap-2 text-black">
						{data && (
							<ResponsiveContainer width="100%" height="100%">
								<LineChart
									data={data}
									margin={{ top: 15, right: 15, left: 15, bottom: 0 }}
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
										stroke="#94a3b8"
										strokeWidth={3}
										yAxisId={1}
										dot={false}
										// dot={{ r: 5, strokeWidth: 2, fill: "#f472b6" }}
										activeDot={{ r: 8 }}
									/>
								</LineChart>
							</ResponsiveContainer>
						)}
					</div>
					<div className="w-40 h-64 bg-white rounded-lg flex items-center justify-center flex-1 flex-col gap-2 text-black">
						{data && (
							<ResponsiveContainer width="100%" height="100%">
								<LineChart
									data={biometrics?.heart_rate}
									margin={{ top: 15, right: 15, left: 15, bottom: 0 }}
								>
									<XAxis dataKey="i" stroke="#8884d8" />
									<YAxis
										yAxisId={1}
										stroke="#8884d8"
										// label={"ur stress 🥺"}
										mirror={true}
										domain={[50, 200]}
										max={200}
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
										dataKey="rate"
										stroke="#94a3b8"
										strokeWidth={3}
										yAxisId={1}
										dot={false}
										// dot={{ r: 5, strokeWidth: 2, fill: "#f472b6" }}
										activeDot={{ r: 8 }}
									/>
								</LineChart>
							</ResponsiveContainer>
						)}
					</div>
				</div>

				<p className="text-slate-400 text-center italic">
					Blood Pressure:{" "}
					<strong>
						{biometrics?.blood_pressure_high} / {biometrics?.blood_pressure_low}
					</strong>
					, Body Temperature: <strong>{biometrics?.body_temperature}</strong>
				</p>

				{/* <div>
					{biometrics && (
						<div className="flex gap-2">
							<Number
								number={`💓 ${Math.round(
									biometrics?.heart_rate[biometrics?.heart_rate.length - 1]
								)}`}
							/>
							<Number
								number={`🩸 ${Math.round(
									biometrics?.blood_pressure_high
								)} / ${Math.round(biometrics?.blood_pressure_low)}`}
							/>
							<Number
								number={`🌡️ ${Math.round(biometrics?.body_temperature)}`}
							/>
						</div>
					)}
				</div> */}
			</div>

			<p className="text-gray-400 text-center italic mt-12">
				I'm looking out for you. 🥺
			</p>

			<div className="w-full flex flex-col items-center gap-4 pb-20">
				{actions &&
					actions.map((action: any, index) => (
						<Action
							action={action}
							data={data}
							biometrics={biometrics}
							key={index}
						/>
					))}
			</div>
		</div>
	);
};

function Action({
	action,
	data,
	biometrics,
}: {
	action: any;
	data?: any[];
	biometrics?: any;
}) {
	console.log(biometrics?.heart_rate);
	return (
		<div className="flex w-[50rem] bg-slate-100 rounded-lg p-4 gap-4">
			<div className="flex flex-1 flex-col gap-4">
				<p className="font-semibold italic text-black">
					{action.condition_cute}
				</p>
				<ul className="text-black space-y-1 pl-4">
					{action.actions_cute.map((action: string, index: number) => (
						<li key={index} className="list-none">
							🖤 {action}
						</li>
					))}
				</ul>
				<div className="flex flex-row justify-between">
					<p className="italic text-slate-400 text-right">
						<strong>Priority:</strong> {action.priority_cute}
					</p>
					<p className="italic text-slate-400 text-right">
						<strong>Executed:</strong> twice
					</p>
				</div>
			</div>
		</div>
	);
}

function Number({ number }: { number: any }) {
	return (
		<div className="flex gap-2 bg-slate-200 rounded-lg p-2">
			<p className="text-gray-700">{number}</p>
		</div>
	);
}

function MotherAvatar() {
	const { x, y } = useMousePosition();
	const { width, height } = useWindowDimensions();
	const ref = useRef<HTMLDivElement>(null);
	const clientRect = useClientRect(ref);

	let cx = 0;
	let cy = 0;
	let dx = 0;
	let dy = 0;
	let transformX = 0;
	let transformY = 0;
	if (clientRect && x && y) {
		cx = clientRect?.left + clientRect?.width / 2;
		cy = clientRect?.top + clientRect?.height / 2;

		dx = x - cx;
		dy = y - cy;

		transformX = (dx / width) * 10;
		transformY = (dy / height) * 10;
	}

	return (
		<div className="relative rounded-lg overflow-hidden w-48 h-48" ref={ref}>
			<img
				src="/ai_mom_eyes.webp"
				alt="Mother Eyes"
				className="w-48 absolute top-0 left-0"
				style={{ transform: `translate(${transformX}px, ${transformY}px)` }}
			/>
			<img
				src="/ai_mom_eyeshadow.webp"
				alt="Mother Eyeshadow"
				className="w-48 absolute top-0 left-0"
			/>
			<img
				src="/ai_mom_fore.webp"
				alt="Mother Face"
				className="w-48 absolute top-0 left-0"
			/>
		</div>
	);
}

export default page;
