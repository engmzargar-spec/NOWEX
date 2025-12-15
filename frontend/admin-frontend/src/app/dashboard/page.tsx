import AdminLayout from "@/components/layout/AdminLayout";

export default function DashboardPage() {
  return (
    <AdminLayout>
      <div className="text-2xl font-semibold mb-4">
        Dashboard
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-lg shadow-md bg-white/10 backdrop-blur-md">
          <h3 className="text-lg font-medium mb-2">Total Users</h3>
          <p className="text-3xl font-bold">1,240</p>
        </div>

        <div className="p-6 rounded-lg shadow-md bg-white/10 backdrop-blur-md">
          <h3 className="text-lg font-medium mb-2">Active Trades</h3>
          <p className="text-3xl font-bold">87</p>
        </div>

        <div className="p-6 rounded-lg shadow-md bg-white/10 backdrop-blur-md">
          <h3 className="text-lg font-medium mb-2">Revenue</h3>
          <p className="text-3xl font-bold">$12,430</p>
        </div>
      </div>
    </AdminLayout>
  );
}
