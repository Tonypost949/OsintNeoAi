import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { X } from "lucide-react";

interface EntityFilterProps {
  onFilterChange: (filters: FilterState) => void;
}

export interface FilterState {
  searchText: string;
  entityTypes: {
    person: boolean;
    email: boolean;
    phone: boolean;
  };
  minConnections: number;
  maxConnections: number;
  minFileCount: number;
  maxFileCount: number;
  dateRange: {
    from?: Date;
    to?: Date;
  };
}

const DEFAULT_FILTERS: FilterState = {
  searchText: "",
  entityTypes: {
    person: true,
    email: true,
    phone: true,
  },
  minConnections: 0,
  maxConnections: 100,
  minFileCount: 0,
  maxFileCount: 1000,
  dateRange: {},
};

export default function EntityFilter({ onFilterChange }: EntityFilterProps) {
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleSearchChange = (text: string) => {
    const newFilters = { ...filters, searchText: text };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleTypeToggle = (type: "person" | "email" | "phone") => {
    const newFilters = {
      ...filters,
      entityTypes: {
        ...filters.entityTypes,
        [type]: !filters.entityTypes[type],
      },
    };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleConnectionsChange = (value: number[]) => {
    const newFilters = {
      ...filters,
      minConnections: value[0],
      maxConnections: value[1],
    };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleFileCountChange = (value: number[]) => {
    const newFilters = {
      ...filters,
      minFileCount: value[0],
      maxFileCount: value[1],
    };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleReset = () => {
    setFilters(DEFAULT_FILTERS);
    onFilterChange(DEFAULT_FILTERS);
  };

  const isFiltered =
    filters.searchText !== "" ||
    !filters.entityTypes.person ||
    !filters.entityTypes.email ||
    !filters.entityTypes.phone ||
    filters.minConnections > 0 ||
    filters.maxConnections < 100 ||
    filters.minFileCount > 0 ||
    filters.maxFileCount < 1000;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Filter Entities</CardTitle>
            <CardDescription>
              {isFiltered && `${Object.keys(filters).length} filter(s) applied`}
            </CardDescription>
          </div>
          <div className="flex gap-2">
            {isFiltered && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleReset}
              >
                <X className="w-4 h-4 mr-2" />
                Reset
              </Button>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? "Hide" : "Show"} Filters
            </Button>
          </div>
        </div>
      </CardHeader>

      {isExpanded && (
        <CardContent className="space-y-6">
          {/* Search */}
          <div>
            <Label htmlFor="search" className="mb-2 block">
              Search by Name
            </Label>
            <Input
              id="search"
              placeholder="Search entities..."
              value={filters.searchText}
              onChange={(e) => handleSearchChange(e.target.value)}
            />
          </div>

          {/* Entity Types */}
          <div>
            <Label className="mb-3 block font-medium">Entity Types</Label>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Checkbox
                  id="type-person"
                  checked={filters.entityTypes.person}
                  onCheckedChange={() => handleTypeToggle("person")}
                />
                <Label htmlFor="type-person" className="font-normal cursor-pointer">
                  People
                </Label>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  id="type-email"
                  checked={filters.entityTypes.email}
                  onCheckedChange={() => handleTypeToggle("email")}
                />
                <Label htmlFor="type-email" className="font-normal cursor-pointer">
                  Emails
                </Label>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  id="type-phone"
                  checked={filters.entityTypes.phone}
                  onCheckedChange={() => handleTypeToggle("phone")}
                />
                <Label htmlFor="type-phone" className="font-normal cursor-pointer">
                  Phone Numbers
                </Label>
              </div>
            </div>
          </div>

          {/* Connections Range */}
          <div>
            <Label className="mb-3 block font-medium">
              Connection Strength: {filters.minConnections} - {filters.maxConnections}
            </Label>
            <Slider
              value={[filters.minConnections, filters.maxConnections]}
              onValueChange={handleConnectionsChange}
              min={0}
              max={100}
              step={1}
              className="w-full"
            />
          </div>

          {/* File Count Range */}
          <div>
            <Label className="mb-3 block font-medium">
              File Appearances: {filters.minFileCount} - {filters.maxFileCount}
            </Label>
            <Slider
              value={[filters.minFileCount, filters.maxFileCount]}
              onValueChange={handleFileCountChange}
              min={0}
              max={1000}
              step={10}
              className="w-full"
            />
          </div>
        </CardContent>
      )}
    </Card>
  );
}
