from dynamic_preferences.types import LongStringPreference, IntPreference
from dynamic_preferences.registries import global_preferences_registry

# Generally, these messages should not be changed here, and instead should be changed in the
# admin section of the website. Only the initial defaults are stored here.

@global_preferences_registry.register
class FarmInfo(LongStringPreference):
    name = 'farm_info'
    default = '''
<a href="https://goo.gl/maps/a6u7WQRRvqu">
    8345 S. Barnards Rd.<br>
    Canby, OR 97013
</a><br>
<a href="tel:503-651-2622">503-651-2622</a><br>
<br>
<b>Open Hours</b><br>
U-pick vegetables and fruit: 8am-4pm Wed-Sun<br>
Pre-picked pickup: 9am-4pm all days<br>
Berry plant sales by appointment all year<br>
        '''


@global_preferences_registry.register
class Prices(LongStringPreference):
    name = 'prices'
    default = '''
<b>For U-Pick Blueberries</b><br>
$1.60 per pound.'''


@global_preferences_registry.register
class AboutMessage(LongStringPreference):
    name = 'about_message'
    default = '''
<p>Our nursery is open now Fri & Sat 9-5 and by appointment for 23 varieties of blueberries 
and other berry plants in 1, 3, 7, 10 and 25 gallon containers. Call 503-730-4788 for nursery 
sales. Check or cash and bring your mud boots.'''


@global_preferences_registry.register
class SeasonStartDay(IntPreference):
    name = 'season_start_day'
    default = 24

@global_preferences_registry.register
class SeasonEndDay(IntPreference):
    name = 'season_end_day'
    default = 15

@global_preferences_registry.register
class OutOfSeasonMessage(LongStringPreference):
    name = 'out_of_season_message'
    default = '''
        Come back here in June to order pre-picked blueberries.
        Until then, you can <a
        href="https://www.tricountyfarm.org/farm/morning-shade-farm-and-berry-nursery">
            visit the farm info page</a> for plant sales and other info.
    '''
