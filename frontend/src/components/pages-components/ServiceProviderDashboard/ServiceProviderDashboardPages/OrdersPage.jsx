import React from "react";
import { useSelector, useDispatch } from "react-redux";
import Container from "../../../shared-components/container/Container";
import HomeOrdersTable from "../../Home/HomeOrdersTable/HomeOrdersTable";
import Spinner from "../../../shared-components/Spinner/Spinner";
import { getAllOrdersAdmin } from "../../../actions/ordersActions";
import { useEffect } from "react";
const OrdersPage = () => {
  const allOrdersAdmin = useSelector((state) => state.allOrdersAdmin);
  const dispatch=useDispatch();
  useEffect(() => {
    dispatch(getAllOrdersAdmin());
  }, [dispatch]);
  const order = allOrdersAdmin
  const {orders,loading} = order;
  return (
    <div className="py-5">
      <Container>
        <h1>
          My <span className="mineTextOrange">Orders</span>
        </h1>
        {loading ? (
          <Spinner />
        ) : (
          <>
       {   
            orders? ( orders?.length === 0 ? (
              <h5 className="text-center">You have no Orders</h5>
            ) : (
              <>
                <HomeOrdersTable orders={orders} />
              </>
            )) : <p className="p-3  text-black rounded">No Orders</p>
          
           }
          </>
        )}
      </Container>
    </div>
  );
};
  

export default OrdersPage;
