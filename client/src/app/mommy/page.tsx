"use client";

import { useEffect, useState } from "react";
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

const page = (props: Props) => {
	const [data, setData] = useState<any[]>();
	useEffect(() => {
		// fetch data from localhost 5000
		fetch("http://127.0.0.1:5000/history")
			.then((res) => res.json())
			.then((data) => {
				console.log(data);
				setData(data);
			});
	}, []);

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

				<div className="w-[40rem] bg-pink-100 rounded-lg p-4">
					<input
						className="w-full bg-transparent outline-none text-black"
						placeholder="type something babyyy..."
					></input>
				</div>
			</div>

			<div className="w-full flex flex-col items-center gap-8 pb-20">
				{/* First Card */}
				<div className="flex w-[50rem] bg-pink-100 rounded-lg p-4 gap-4">
					<div className="flex-1">
						<p className="font-semibold italic text-black">
							<span className="font-bold">
								when the news feels heavy and your heart starts to race...
							</span>{" "}
							~ 💞🕊️
						</p>
						<ul className="mt-2 text-gray-700 space-y-1">
							<li>🐱 pull up videos of cute little kitties for you, uwu~ ✨</li>
							<li>
								🌐 search the web for happy little stories in the world, just
								for you 💗
							</li>
						</ul>
					</div>
					<div className="w-40 h-64 bg-white rounded-lg flex items-center justify-center flex-1">
						{/* Placeholder for Graph */}
						{/* <p className="text-sm text-gray-500">
							📈 ur stress after last activation 😅
						</p> */}

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
					</div>
				</div>

				{/* Second Card */}
				<div className="flex w-[50rem] bg-pink-100 rounded-lg p-4 gap-4">
					<div className="flex-1">
						<p className="font-semibold italic text-black">
							<span className="font-bold">when you're feeling lonely...</span> ~
							🪽🌙
						</p>
						<ul className="mt-2 text-gray-700 space-y-1">
							<li>📜 find text messages from ur loved ones</li>
							<li>🥰 play mommy asmr on youtube</li>
						</ul>
					</div>
					<div className="w-40 h-64 bg-white rounded-lg flex items-center justify-center flex-1">
						{/* Placeholder for Graph */}
						{/* <p className="text-sm text-gray-500">📉 stress over time</p> */}
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
					</div>
				</div>
			</div>
		</div>
	);
};

export default page;
