"use client";

import * as Toast from "@radix-ui/react-toast";
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";
import { createContext, useContext, useState, useCallback, useRef, useEffect, type ReactNode } from "react";

interface ToastData {
  id: string;
  title: string;
  description?: string;
  variant?: "success" | "error" | "info" | "warning";
}

interface ToastContextType {
  show: (data: Omit<ToastData, "id">) => void;
}

const ToastContext = createContext<ToastContextType>({ show: () => {} });

export function useToast() {
  return useContext(ToastContext);
}

const icons = {
  success: CheckCircle,
  error: AlertCircle,
  info: Info,
  warning: AlertTriangle,
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastData[]>([]);
  const timersRef = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map());

  useEffect(() => {
    const timers = timersRef.current;
    return () => {
      timers.forEach((t) => clearTimeout(t));
      timers.clear();
    };
  }, []);

  const show = useCallback((data: Omit<ToastData, "id">) => {
    const id = Math.random().toString(36).slice(2);
    setToasts((prev) => [...prev, { ...data, id }]);
    const timer = setTimeout(() => {
      timersRef.current.delete(id);
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
    timersRef.current.set(id, timer);
  }, []);

  const remove = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ show }}>
      <Toast.Provider swipeDirection="right">
        {children}
        {toasts.map((t) => {
          const IconComp = icons[t.variant || "info"] || Info;
          return (
            <Toast.Root
              key={t.id}
              className={cn(
                "glass rounded-2xl border p-4 shadow-lg shadow-black/10",
                "data-[state=open]:animate-in data-[state=closed]:animate-out",
                "data-[swipe=end]:animate-out",
                "flex items-start gap-3 min-w-[320px]",
              )}
              onOpenChange={(open) => !open && remove(t.id)}
            >
              <IconComp
                className={cn(
                  "h-5 w-5 mt-0.5 shrink-0",
                  t.variant === "success" && "text-success",
                  t.variant === "error" && "text-danger",
                  t.variant === "warning" && "text-warning",
                  (!t.variant || t.variant === "info") && "text-primary",
                )}
              />
              <div className="flex-1 min-w-0">
                <Toast.Title className="text-sm font-medium">
                  {t.title}
                </Toast.Title>
                {t.description && (
                  <Toast.Description className="text-xs text-muted-foreground mt-0.5">
                    {t.description}
                  </Toast.Description>
                )}
              </div>
              <Toast.Close className="shrink-0 rounded-lg p-1 text-muted-foreground hover:text-foreground transition-colors">
                <X className="h-4 w-4" />
              </Toast.Close>
            </Toast.Root>
          );
        })}
        <Toast.Viewport className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-[420px]" />
      </Toast.Provider>
    </ToastContext.Provider>
  );
}
