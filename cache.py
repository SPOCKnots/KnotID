
from peewee import *
import os


directory = os.path.dirname(os.path.realpath(__file__)) + '/cache.db'
DB_LOCATION = directory
# The location of the database to work with.

db = SqliteDatabase(DB_LOCATION)
db.connect()


class BaseModel(Model):
    class Meta(object):
        database = db

class CachedGaussCode(BaseModel):
    '''Peewee model for storing cached knot data.'''

    gauss_code = CharField()

    num_crossings = IntegerField(null=True)

    alexander = CharField(null=True)

    determinant = IntegerField(null=True)

    alex_imag_3 = IntegerField(null=True)

    alex_imag_4 = IntegerField(null=True)

    vassiliev_degree_2 = IntegerField(null=True)

    vassiliev_degree_3 = IntegerField(null=True)

    hyperbolic_volume = CharField(null=True)

    identification = CharField(null=True)

    is_virtual = BooleanField(null=True)

    self_linking = BooleanField(null=True)

if __name__ == "__main__":
    import sys
    import os
    if len(sys.argv) == 1:
        print('No mode specified.')
        exit()

    mode = sys.argv[1]
    if mode == 'reset':
        db.connect()
        num_cached = CachedGaussCode.select().count()
        db.close()

        os.remove('cache.db')
        db.connect()
        CachedGaussCode.create_table()
        num_after = CachedGaussCode.select().count()
        db.close()
        print('Reset database, went from {} to {} cached.'.format(
            num_cached, num_after))
        exit()

    print('Invalid mode specified. Should be "reset".')
    
        
    
        
