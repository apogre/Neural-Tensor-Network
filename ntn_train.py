from load_params import *
from neuralTensorNetwork import *


def neuralTensorNetwork():

    print(""" Get the program parameters """)
    program_parameters = getProgramParameters()

    print(""" Extract information useful within the scope of this function """)
    num_iterations = program_parameters['num_iterations']
    batch_size = program_parameters['batch_size']
    corrupt_size = program_parameters['corrupt_size']
    batch_iterations = program_parameters['batch_iterations']
    data_set = program_parameters['data_set']
    w_param = program_parameters['w_param']
    if data_set == 0:
        data_set = 'data/Wordnet/'
    elif data_set == 1:
        data_set = 'data/Freebase/'
    else:
        data_set = 'data/DBpedia/'
    print data_set
    print(""" Get entity and relation data dictionaries """)
    entity_dictionary, num_entities = getDictionary(data_set+'entities.txt')
    relation_dictionary, num_relations = getDictionary(data_set+'relations.txt')

    print(""" Get training data using entity and relation dictionaries """)
    training_data, num_training_examples = getTrainingData(data_set+'train.txt', entity_dictionary, relation_dictionary)

    print(""" Get word indices for all the entities in the data """)
    word_indices, num_words = getWordIndices(data_set+'wordIndices.p')

    print(""" Store newly learned data in the dictionary """)

    program_parameters['num_entities'] = num_entities
    program_parameters['num_relations'] = num_relations
    program_parameters['num_training_examples'] = num_training_examples
    program_parameters['num_words'] = num_words
    program_parameters['word_indices'] = word_indices

    print(""" Create a NeuralTensorNetwork object """)

    network = NeuralTensorNetwork(program_parameters)

    start_time = datetime.datetime.now()
    for i in range(num_iterations):
        print i
        # print(""" Create a training batch by picking up random samples from training data """)
        print str(start_time)

        batch_indices = np.random.randint(num_training_examples, size=batch_size) #Randomly sample training batch

        data = dict()
        data['rel'] = np.tile(training_data[batch_indices, 1], (1, corrupt_size)).T
        data['e1'] = np.tile(training_data[batch_indices, 0], (1, corrupt_size)).T

        data['e2'] = np.tile(training_data[batch_indices, 2], (1, corrupt_size)).T
        data['e3'] = np.random.randint(num_entities, size=(batch_size * corrupt_size, 1))


        print(""" Optimize the network using the training batch """)

        if np.random.random() < 0.5:
            opt_solution = scipy.optimize.minimize(network.neuralTensorNetworkCost, network.theta, args=(data, 0,),\
                                                   method='L-BFGS-B', jac=True, options={'maxiter': batch_iterations})
        else:
            opt_solution = scipy.optimize.minimize(network.neuralTensorNetworkCost, network.theta, args=(data, 1,), \
                                                   method='L-BFGS-B', jac=True, options={'maxiter': batch_iterations})
        # print opt_solution
        print(""" Store the optimized theta value """)

        #self.stackToParams(W, V, b, U, word_vectors)
        network.theta = opt_solution.x

    print(""" Get test data to calculate predictions """)

    dev_data, dev_labels = getTestData(data_set+'dev.txt', entity_dictionary, relation_dictionary)

    test_data, test_labels = getTestData(data_set+'test.txt', entity_dictionary, relation_dictionary)

    print(""" Compute the best thresholds for classification, and get predictions on test data """)
    
    network.computeBestThresholds(dev_data, dev_labels, data_set)

    predictions = network.getPredictions(test_data)

    """ Print accuracy of the obtained predictions """

    print "Accuracy:", np.mean((predictions == test_labels))
    accuracy = np.mean((predictions == test_labels))
    f = open('accuracy.txt', 'a')
    f.write(str(datetime.datetime.now()) + '\t' + str(accuracy)+'\n')
    f.close()


neuralTensorNetwork()
