# Ask
def remove_redundancy(queriedString):
    try:
        ids = [ i['_id'] for i in database.find({ "entity_name" : {'$regex' : '.*{}.*'.format(queriedString), '$options' : 'i'} })]
        try:
            _ = database.delete_many({'_id': {'$in' : ids[1:]} })
        except Exception as e:            
            print(e)
            return

    except Exception as e:
        print(e)
        return
