import dataloader
import dataprocessor
import mdp
import numpy

def main():
    group_by = 120
    order = 2
    dl = dataloader.DataLoader()
    min_t, max_t =  dl.get_min_max_timestamps()
    start_t = min_t
    stop_t = start_t + group_by
    
    
    lnode = mdp.nodes.LinearRegressionNode(use_pinv = True)
    
    
    
    while stop_t <= max_t:
        count, timedata_and_people = dl.load_data_bundle(start_t, stop_t)
        if count >= 3:
            time_and_data = []
            people = []
            for t, p in timedata_and_people:
                time_and_data.append(t)
                people.append(p)
        uz_data = dataprocessor.unzip_data_bundle(time_and_data)
        time_and_feats = dataprocessor.extract_all_features_from_sensors(uz_data)
        _time, pols = dataprocessor.build_polynomial_features(time_and_feats, order=order)
        pols = pols[:,1:]
        
        arr_people = numpy.array(people, dtype="float64")
        p = numpy.empty( [1, 1] )
        p[0][0] = numpy.average(arr_people)

        print p
        print pols
        lnode.train(pols, p)
        start_t = stop_t + 1
        stop_t = start_t + group_by
        
    print "stopping training"
    lnode.stop_training()
    print "training_stopped"
    

    start_t = min_t
    stop_t = start_t + group_by

    store = []
    avg_abs_err = 0
    total = 0
    
    nz_total = 0
    nz_avg_abs_err = 0
    

    while stop_t <= max_t:
        count, timedata_and_people = dl.load_data_bundle(start_t, stop_t)
        if count >= 3:
            time_and_data = []
            people = []
            for t, p in timedata_and_people:
                time_and_data.append(t)
                people.append(p)
        uz_data = dataprocessor.unzip_data_bundle(time_and_data)
        time_and_feats = dataprocessor.extract_all_features_from_sensors(uz_data)
        _time, pols = dataprocessor.build_polynomial_features(time_and_feats, order=order)
        pols = pols[:,1:]
        
        arr_people = numpy.array(people, dtype="float64")
        p = numpy.empty( [1, 1] )
        p[0][0] = numpy.average(arr_people)

        p_est = lnode.execute(pols)
        
        print "True:", p, "estimate:", p_est
        
        if p[0][0] != 0:
            store.append((p, p_est))
            nz_total += 1
            nz_avg_abs_err += abs(p[0][0] -p_est[0][0]) 
            
            
        total += 1
        avg_abs_err += abs(p[0][0] -p_est[0][0]) 
        
        start_t = stop_t + 1
        stop_t = start_t + group_by



    for tr, est in store:
        print "True:", tr, "estimate:", est
        
    print "Total:", total
    print "Average error:", avg_abs_err/float(total)
    print "Total non-zeros:",  nz_total
    print "Average error on non-zeros:", nz_avg_abs_err/float(nz_total)
    
    
if __name__ == "__main__":
    main()