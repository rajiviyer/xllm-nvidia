import type { Config } from "tailwindcss";
import typography from "@tailwindcss/typography"; // Import the plugin

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
      colors: {
        khaki: "#A49E8D",
        pale_dogwood: "#DEC3BE",
        slate_gray: "#6B7F82",
        air_superiority_blue: "#7C99B4",
        beaver: "#A29587",
        coyote: "#846C5B",
        battleship_gray: "#7C898B",
        mountbatten_pink: "#A6808C",
        timber_wolf: "#D6CFCB",
        cal_polygreen: "#2C5530",
        viridian: "#668F80",
        princeton_orange: "#FF9933",
        atomic_tangerine: "#F79F79",
        sunset: "#F7D08A",
        gunmetal: "#292F36",
        prussianblue: "#13293D",
        midnightgreen: "#023436",
        mahogany: "#C44900",
        rosewood: "#5A0001",
        junglegreen: "#419D78",
        hunyadiyellow: "#ECA72C",
        bondingai_primary: "#111216",
        bondingai_secondary: "#D7B879",
        bondingai_input: "#1C2230",
        bondingai_input_border: "#FFFFFF99",
        bondingai_input_label: "#FFFFFF",
        bondingai_input_text: "#667085",
        bondingai_card: "#19213600",
      },
    },
    plugins: [typography],
  },
};
export default config;
