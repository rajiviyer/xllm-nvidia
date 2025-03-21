import "./globals.css";
import Navbar from "@/components/Navbar";
import { Inter } from "next/font/google";
import type { Metadata } from "next";
// import { EmbeddingsContextProvider } from "@/app/_context/EmbeddingsContext";
import { DataPropsContextProvider } from "./_context/DataPropsContext";
import { FormDataContextProvider } from "./_context/FormDataContext";

const inter = Inter({ subsets: ["latin"], weight: ["400", "700"] });
export const metadata: Metadata = {
  title: "XLLM Project",
  description: "Built using Next.js with Typescript & TailwindCSS",
  keywords: "Next.js Typescript TailwindCSS",
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <FormDataContextProvider>
      <DataPropsContextProvider>
        <html lang="en">
          <body className={inter.className}>
            <Navbar />
            <main className="bg-bondingai_primary">{children}</main>
          </body>
        </html>
      </DataPropsContextProvider>
    </FormDataContextProvider>
  );
}
