import React, { useEffect } from "react";
import { FaWarehouse } from "react-icons/fa";
import { Link } from "react-router-dom";
import StorageUnitsTable from "../ServiceProviderDashboardComponents/StorageUnitsPageComponents/StorageUnitsTable";
import Spinner from "../../../shared-components/Spinner/Spinner";
import { useDispatch, useSelector } from "react-redux";
import { getTotalStorageUnits } from "../../../actions/storageUnitActions";
import StorageUnitsRoomsTable from "../ServiceProviderDashboardComponents/StorageProviderDetailsPageComponents/StorageUnitRoomsTable";

const EmployeesPage = () => {
  const dispatch = useDispatch();

  const { loading, storageUnits } = useSelector(
    (state) => state.getTotalStorageUnit
  );

  useEffect(() => {
    dispatch(getTotalStorageUnits());
  }, [dispatch]);

  return (
    <>
      {loading ? (
        <Spinner />
      ) : (
        <div className="mt-3">
          <div className="align-items-center d-none d-lg-flex justify-content-between">
            <div className="d-flex align-items-center">
              <div className="p-2 bg-orange text-light rounded me-2">
                <FaWarehouse size={20} />
              </div>
              <h5 className="text-uppercase">Storage Units</h5>
            </div>
            <div>
              <Link
                to="/service-provider-dashboard/addUnit"
                className="btn btn-dark"
              >
                ADD NEW UNIT
              </Link>
            </div>
          </div>

          <div className="card mt-4">
            <div className="card-body">
              <h5 className="text-muted">Page</h5>
              <h3>All Storage Units</h3>
              <StorageUnitsRoomsTable storageUnits={storageUnits} />
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default EmployeesPage;
