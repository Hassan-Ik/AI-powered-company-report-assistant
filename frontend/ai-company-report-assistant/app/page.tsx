/* File: /app/page.tsx */

"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { motion } from "framer-motion";
import { Loader2, Upload, FileText, MessageSquare } from "lucide-react";
import { ReactNode } from "react";

type Message = {
  role: "user" | "assistant";
  content: string | ReactNode;
};

export default function Home() {
  const [reportFile, setReportFile] = useState<File | null>(null);
  const [guidelinesFile, setGuidelinesFile] = useState<File | null>(null);
  const [text, setText] = useState<string>("");
  const [guidelinesText, setGuidelinesText] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [messages, setMessages] = useState<Message[]>([]);

  const handleSubmit = async () => {
  setLoading(true);
  setMessages((prev) => [
    ...prev,
    {
      role: "user",
      content:
        "Please analyze this company report and provide key metrics and actionable insights.",
    },
  ]);

  try {
    const formData = new FormData();
    if (reportFile) formData.append("report_file", reportFile);
    if (guidelinesFile) formData.append("guidelines_file", guidelinesFile);
    if (text) formData.append("text", text);
    if (guidelinesText) formData.append("guidelines_text", guidelinesText);

    const res = await fetch("/api/proxy", {
      method: "POST",
      body: formData,
    });
    const result = await res.json();
    console.log(result);

    if (result.success && result.data) {
      const {
        important_metrics,
        summary,
        review,
        company_name,
        report_type,
        year,
      } = result.data;

      if (important_metrics && Object.keys(important_metrics).length > 0) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `Here are the extracted metrics from your ${report_type} report for ${company_name} (${year}):`,
          },
          {
            role: "assistant",
            content: (
              <pre className="bg-gray-100 p-2 rounded overflow-x-auto">
                {JSON.stringify(important_metrics, null, 2)}
              </pre>
            ),
          },
        ]);
      }

      if (summary) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: `Here’s a quick summary for you:` },
          { role: "assistant", content: summary },
        ]);
      }

      if (review) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: `Here’s an analyst review based on the report:`,
          },
          { role: "assistant", content: review },
        ]);
      }

      if (result.meta) {
        const { processing_time_seconds, has_guidelines } = result.meta;

        if (processing_time_seconds) {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: `⏱️ Analysis completed in ${processing_time_seconds.toFixed(
                2
              )} seconds.`,
            },
          ]);
        }

        if (has_guidelines) {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: `📘 Guidelines were included in the analysis.`,
            },
          ]);
        }
      }
    } else {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Error: ${result.error || "Unknown error occurred."}`,
        },
      ]);
    }
  } catch (err) {
    console.error(err);
    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: "Failed to fetch results." },
    ]);
  } finally {
    setLoading(false);
  }
};


  return (
    <div className="min-h-screen p-8 bg-purple-100 flex flex-col items-center">
      <motion.div
  initial={{ opacity: 0, y: -30 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.8, ease: "easeOut" }}
  className="flex flex-col items-center"
>
  <motion.h1
  className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-700 to-red-500 text-center"
>
  AI Powered Company Report Assistant
</motion.h1>

<p
  className="text-gray-700 max-w-xl my-3 text-center text-base md:text-md"
>
  Your AI Assistant to quickly summarize company reports, extract key metrics, and provide actionable insights—making complex data clear, transparent, and easy to act on for teams, investors, and employees.
</p>
  {/* <motion.img
    src="/assistant.png" // replace with your image path
    alt="Assistant"
    className="w-36 h-36 object-contain"
    initial={{ opacity: 0, scale: 0.8 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ duration: 0.6, delay: 0.2, ease: "easeOut" }}
  /> */}
</motion.div>

<Card className="w-full max-w-2xl mb-6 shadow-lg rounded-lg border border-gray-200">
  <CardContent className="space-y-6 p-6">
    
    {/* Upload Report */}
    <div className="flex flex-col">
  <div className="flex items-center gap-2">
    <label
      htmlFor="report-upload"
      className="flex items-center gap-2 font-medium text-gray-700 cursor-pointer border border-gray-300 rounded-md px-3 py-2 hover:border-gray-400"
    >
      <Upload size={18} />
      {reportFile ? reportFile.name : "Upload Report (PDF)"}
    </label>

    {reportFile && (
      <button
        type="button"
        onClick={() => setReportFile(null)}
        className="text-gray-500 hover:text-red-500"
      >
        ✕
      </button>
    )}
  </div>

  <input
    id="report-upload"
    type="file"
    accept="application/pdf"
    onChange={(e) => setReportFile(e.target.files?.[0] ?? null)}
    className="hidden"
  />
</div>

    {/* Paste Report Text */}
    <div className="flex flex-col">
      <label className="flex items-center gap-2 font-medium text-gray-700 mb-1">
        <FileText size={18} /> Or Paste Report Text
      </label>
      <textarea
        className="w-full border border-gray-600 rounded-md p-3 placeholder-gray-500 text-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-500"
        rows={5}
        placeholder="Paste the report content here..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
    </div>

    {/* Upload Guidelines */}
    <div className="flex flex-col">
  <div className="flex items-center gap-2">
    <label
      htmlFor="guidelines-upload"
      className="flex items-center gap-2 font-medium text-gray-700 cursor-pointer border border-gray-300 rounded-md px-3 py-2 hover:border-gray-400"
    >
      <Upload size={18} />
      {guidelinesFile ? guidelinesFile.name : "Upload Guidelines (PDF)"}
    </label>

    {guidelinesFile && (
      <button
        type="button"
        onClick={() => setGuidelinesFile(null)}
        className="text-gray-500 hover:text-red-500"
      >
        ✕
      </button>
    )}
  </div>

  <input
    id="guidelines-upload"
    type="file"
    accept="application/pdf"
    onChange={(e) => setGuidelinesFile(e.target.files?.[0] ?? null)}
    className="hidden"
  />
</div>


    {/* Paste Guidelines Text */}
    <div className="flex flex-col">
      <label className="flex items-center gap-2 font-medium text-gray-700 mb-1">
        <FileText size={18} /> Or Paste Guidelines Text
      </label>
      <textarea
        className="w-full border border-gray-300 rounded-md p-3 placeholder-gray-500 text-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-500"
        rows={3}
        placeholder="Paste the guidelines content here..."
        value={guidelinesText}
        onChange={(e) => setGuidelinesText(e.target.value)}
      />
    </div>

    {/* Submit Button */}
    <Button
      onClick={handleSubmit}
      disabled={loading}
      className="w-full flex items-center justify-center gap-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-md py-2"
    >
      {loading ? <Loader2 className="animate-spin" /> : <MessageSquare />}
      {loading ? "Analyzing..." : "Ask Assistant"}
    </Button>

  </CardContent>
</Card>


<div className="w-full max-w-2xl space-y-4">
  {messages.map((msg, i) => (
    <motion.div
      key={i}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`relative p-4 rounded-lg shadow text-sm whitespace-pre-line border ${
        msg.role === "assistant"
          ? "bg-purple-50 border-purple-400 text-purple-900"
          : "bg-purple-300 border-purple-600 text-purple-900"
      }`}
    >
      <strong className="mr-2">
        {msg.role === "assistant"
          ? "Assistant"
          : "You"}:
      </strong>
      {msg.content}

      {/* Remove button */}
      <button
        onClick={() => {
          const newMessages = [...messages];
          newMessages.splice(i, 1);
          setMessages(newMessages);
        }}
        className="absolute top-1 right-2 text-gray-600 hover:text-red-600 font-bold"
      >
        ✕
      </button>
    </motion.div>
  ))}
</div>


    </div>
  );
}
