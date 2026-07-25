import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, Trash2, Plus } from "lucide-react";
import { toast } from "sonner";
import { trpc } from "@/lib/trpc";

interface GoogleDriveConnectProps {
  analysisId: number;
}

export default function GoogleDriveConnect({ analysisId }: GoogleDriveConnectProps) {
  const [isConnecting, setIsConnecting] = useState(false);

  const accountsQuery = trpc.googleDrive.listAccounts.useQuery();
  const disconnectMutation = trpc.googleDrive.disconnectAccount.useMutation();
  const scanMutation = trpc.googleDrive.scanAndAddFiles.useMutation();
  const utils = trpc.useUtils();

  const handleConnect = async () => {
    try {
      setIsConnecting(true);
      const result = await utils.googleDrive.getAuthUrl.fetch();
      if (result.authUrl) {
        window.open(result.authUrl, "google-oauth", "width=500,height=600");
        setTimeout(() => {
          accountsQuery.refetch();
        }, 2000);
      }
    } catch (error) {
      toast.error("Failed to get authorization URL. Google Drive integration may not be configured.");
    } finally {
      setIsConnecting(false);
    }
  };

  const handleDisconnect = async (accountId: number) => {
    try {
      await disconnectMutation.mutateAsync({ accountId });
      toast.success("Account disconnected");
      accountsQuery.refetch();
    } catch (error) {
      toast.error("Failed to disconnect account");
    }
  };

  const handleScanDrive = async (accountId: number) => {
    try {
      const result = await scanMutation.mutateAsync({
        accountId,
        analysisId,
        maxFiles: 200,
      });
      toast.success(`Added ${result.filesAdded} files from Google Drive`);
      if (result.errors.length > 0) {
        toast.error(`${result.errors.length} files failed to add`);
      }
    } catch (error) {
      toast.error("Failed to scan Google Drive");
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Google Drive Integration</CardTitle>
        <CardDescription>
          Connect your Google Drive account to scan and analyze files
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {accountsQuery.data && accountsQuery.data.length > 0 ? (
          <div className="space-y-3">
            {accountsQuery.data.map((account) => (
              <div
                key={account.id}
                className="flex items-center justify-between p-3 border border-slate-200 rounded-lg"
              >
                <div>
                  <p className="font-medium text-slate-900">{account.email}</p>
                  <p className="text-xs text-slate-500">
                    Connected {new Date(account.createdAt).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="default"
                    onClick={() => handleScanDrive(account.id)}
                    disabled={scanMutation.isPending}
                  >
                    {scanMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Scanning...
                      </>
                    ) : (
                      <>
                        <Plus className="w-4 h-4 mr-2" />
                        Scan & Add Files
                      </>
                    )}
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleDisconnect(account.id)}
                    disabled={disconnectMutation.isPending}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-600 text-center py-4">
            No Google Drive accounts connected
          </p>
        )}

        <Button
          onClick={handleConnect}
          disabled={isConnecting}
          className="w-full"
        >
          {isConnecting ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Connecting...
            </>
          ) : (
            <>
              <Plus className="w-4 h-4 mr-2" />
              Connect Google Drive Account
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}
