"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { AnimatePresence, motion } from "framer-motion";
import { uploadFile } from "../../lib/api";
import { useTutorStore } from "../../stores/tutorStore";
import type { IngestResponse } from "../../lib/types";

interface DropZoneProps {
  onIngested: (result: IngestResponse) => void;
}

export default function DropZone({ onIngested }: DropZoneProps) {
  const sessionId = useTutorStore((state) => state.sessionId);
  const addUploadedFile = useTutorStore((state) => state.addUploadedFile);
  const [uploadingFiles, setUploadingFiles] = useState<string[]>([]);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      for (const file of acceptedFiles) {
        setUploadingFiles((prev) => [...prev, file.name]);
        try {
          const result = await uploadFile(sessionId, file);
          addUploadedFile(result.filename);
          onIngested(result);
        } catch (error) {
          // swallow — DropZone shows no error state, IngestionStatus will simply not list the file
        } finally {
          setUploadingFiles((prev) => prev.filter((name) => name !== file.name));
        }
      }
    },
    [sessionId, addUploadedFile, onIngested]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "text/plain": [".txt"],
    },
  });

  return (
    <div
      {...getRootProps()}
      className={`group relative cursor-pointer overflow-hidden rounded-xl border-2 border-dashed p-6 text-center transition-all duration-200 ${
        isDragActive
          ? "scale-[1.02] border-indigo-400 bg-indigo-500/10"
          : "border-white/15 bg-white/[0.03] hover:border-indigo-400/50 hover:bg-white/[0.06]"
      }`}
    >
      <input {...getInputProps()} />

      <motion.div
        animate={isDragActive ? { y: [-2, 2, -2] } : { y: 0 }}
        transition={{ duration: 1, repeat: isDragActive ? Infinity : 0 }}
        className={`mx-auto mb-2 flex h-11 w-11 items-center justify-center rounded-full text-xl transition-colors ${
          isDragActive
            ? "bg-indigo-500/20 text-indigo-300"
            : "bg-white/5 text-gray-400 group-hover:text-indigo-300"
        }`}
      >
        ⬆
      </motion.div>

      <p className="text-sm font-medium text-gray-200">
        {isDragActive ? "Drop it right here" : "Drag & drop your notes"}
      </p>
      <p className="mt-1 text-xs text-gray-500">PDF, DOCX or TXT · or click to browse</p>

      <AnimatePresence>
        {uploadingFiles.length > 0 && (
          <motion.ul
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-4 space-y-1.5 overflow-hidden"
          >
            {uploadingFiles.map((name) => (
              <li
                key={name}
                className="flex items-center gap-2 rounded-lg bg-indigo-500/10 px-2.5 py-1.5 text-xs text-indigo-200"
              >
                <span className="h-3 w-3 flex-shrink-0 animate-spin rounded-full border-2 border-indigo-400 border-t-transparent" />
                <span className="truncate">{name}</span>
              </li>
            ))}
          </motion.ul>
        )}
      </AnimatePresence>
    </div>
  );
}
