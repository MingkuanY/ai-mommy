import { useState, useEffect, useCallback } from "react";

export function useClientRect<T extends HTMLElement>(
	ref: React.RefObject<T> | React.RefObject<null>
) {
	const [rect, setRect] = useState<DOMRect | null>(null);

	const updateRect = useCallback(() => {
		if (ref && ref.current) {
			setRect(ref.current.getBoundingClientRect());
		}
	}, [ref]);

	useEffect(() => {
		updateRect(); // Initial update

		window.addEventListener("resize", updateRect);
		window.addEventListener("scroll", updateRect, { passive: true });

		return () => {
			window.removeEventListener("resize", updateRect);
			window.removeEventListener("scroll", updateRect);
		};
	}, [updateRect]);

	return rect;
}
