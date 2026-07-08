import { Switch, Route, Router as WouterRouter } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/not-found";
import Layout from "@/components/layout";
import Overview from "@/pages/overview";
import ActorsIndex from "@/pages/actors/index";
import ActorDetail from "@/pages/actors/detail";
import EntitiesIndex from "@/pages/entities/index";
import TimelineIndex from "@/pages/timeline/index";
import MoneyFlowIndex from "@/pages/money-flow/index";
import QuestionsIndex from "@/pages/questions/index";
import NetworkPage from "@/pages/network/index";
import WorkspacePage from "@/pages/workspace/index";

const queryClient = new QueryClient();

function Router() {
  return (
    <Layout>
      <Switch>
        <Route path="/" component={Overview} />
        <Route path="/actors" component={ActorsIndex} />
        <Route path="/actors/:id" component={ActorDetail} />
        <Route path="/entities" component={EntitiesIndex} />
        <Route path="/timeline" component={TimelineIndex} />
        <Route path="/money-flow" component={MoneyFlowIndex} />
        <Route path="/questions" component={QuestionsIndex} />
        <Route path="/network" component={NetworkPage} />
        <Route path="/workspace" component={WorkspacePage} />
        <Route component={NotFound} />
      </Switch>
    </Layout>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
          <Router />
        </WouterRouter>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
