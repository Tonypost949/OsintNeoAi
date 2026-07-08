import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, type LocationInput, type LocationsListResponse } from "@shared/routes";

function parseWithLogging<T>(schema: any, data: unknown, label: string): T {
  const result = schema.safeParse(data);
  if (!result.success) {
    console.error(`[Zod] ${label} validation failed:`, result.error.format());
    throw result.error;
  }
  return result.data;
}

export function useLocations() {
  return useQuery({
    queryKey: [api.locations.list.path],
    queryFn: async () => {
      const res = await fetch(api.locations.list.path, { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch locations");
      const data = await res.json();
      return parseWithLogging<LocationsListResponse>(api.locations.list.responses[200], data, "locations.list");
    },
  });
}

export function useCreateLocation() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: LocationInput) => {
      const validated = api.locations.create.input.parse(data);
      const res = await fetch(api.locations.create.path, {
        method: api.locations.create.method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(validated),
        credentials: "include",
      });
      
      if (!res.ok) {
        if (res.status === 400) {
          const errorData = await res.json();
          throw new Error(errorData.message || "Validation failed");
        }
        throw new Error("Failed to create location");
      }
      
      const responseData = await res.json();
      return api.locations.create.responses[201].parse(responseData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [api.locations.list.path] });
    },
  });
}
