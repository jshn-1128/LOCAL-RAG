"use client";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html>
      <body className="bg-background text-foreground">
        <div className="flex items-center justify-center min-h-screen p-6">
          <div className="text-center space-y-4 max-w-md">
            <h1 className="text-2xl font-bold">Critical Error</h1>
            <p className="text-muted-foreground text-sm">
              {error.message || "Application failed to load"}
            </p>
            <button
              onClick={() => reset()}
              className="px-4 py-2 rounded-xl bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90"
            >
              Reload
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
