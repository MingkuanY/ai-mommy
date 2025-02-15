interface Props {}

const page = (props: Props) => {
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
						<p className="text-sm text-gray-500">
							📈 ur stress after last activation 😅
						</p>
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
						<p className="text-sm text-gray-500">📉 stress over time</p>
					</div>
				</div>
			</div>
		</div>
	);
};

export default page;
