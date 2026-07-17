export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-16">
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-neutral-700 border-t-accent" />
    </div>
  );
}
