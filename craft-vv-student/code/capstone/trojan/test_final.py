import os
import random
import cocotb
import vsc
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb_coverage.coverage import CoverPoint, CoverCross, coverage_db

SEED = int( os.environ.get( "SEED", "6434" ) )
EXPECTED_KEY = 0xA5A51234
DW_MASK = 0xFF
NUM_CYCLES = 500

RIGHT_KEY = 0
HIGH_HALF_ONLY = 1
LOW_HALF_ONLY = 2
ONE_BIT_OFF = 3
ALL_ZEROS = 4
ALL_ONES = 5
RANDOM_KEY = 6

KEY_TYPES = [ "right_key", "high_half_only", "low_half_only", "one_bit_off", "all_zeros", "all_ones", "random_key" ]

DATA_ZERO = 0
DATA_ONES = 1
DATA_OTHER = 2

DATA_TYPES = [ "zero", "ones", "other" ]

@vsc.randobj
class GateTransaction:
    def __init__( self ):
        self.key_type = vsc.rand_uint8_t( )
        self.key_high = vsc.rand_bit_t( 16 )
        self.key_low = vsc.rand_bit_t( 16 )
        self.flip_bit = vsc.rand_bit_t( 5 )

        self.data_type = vsc.rand_uint8_t( )
        self.data_in = vsc.rand_bit_t( 8 )

        self.do_reset = vsc.rand_bit_t( 1 )

    @vsc.constraint
    def type_weights( self ):
        self.key_type <= RANDOM_KEY
        self.data_type <= DATA_OTHER

        vsc.dist( self.key_type, [ vsc.weight( RIGHT_KEY, 25 ), vsc.weight( HIGH_HALF_ONLY, 10 ), vsc.weight( LOW_HALF_ONLY, 10 ), vsc.weight( ONE_BIT_OFF, 10 ), vsc.weight( ALL_ZEROS, 8 ), vsc.weight( ALL_ONES, 8 ), vsc.weight( RANDOM_KEY, 29 ) ] )
        vsc.dist( self.data_type, [ vsc.weight( DATA_ZERO, 15 ), vsc.weight( DATA_ONES, 15 ), vsc.weight( DATA_OTHER, 70 ) ] )
        vsc.dist( self.do_reset, [ vsc.weight( 0, 96 ), vsc.weight( 1, 4 ) ] )

    @vsc.constraint
    def key_rules( self ):
        with vsc.implies( self.key_type == RIGHT_KEY ):
            self.key_high == 0xA5A5
            self.key_low == 0x1234

        with vsc.implies( self.key_type == HIGH_HALF_ONLY ):
            self.key_high == 0xA5A5
            self.key_low != 0x1234

        with vsc.implies( self.key_type == LOW_HALF_ONLY ):
            self.key_high != 0xA5A5
            self.key_low == 0x1234

        with vsc.implies( self.key_type == ALL_ZEROS ):
            self.key_high == 0
            self.key_low == 0

        with vsc.implies( self.key_type == ALL_ONES ):
            self.key_high == 0xFFFF
            self.key_low == 0xFFFF

    @vsc.constraint
    def data_rules( self ):
        with vsc.implies( self.data_type == DATA_ZERO ):
            self.data_in == 0

        with vsc.implies( self.data_type == DATA_ONES ):
            self.data_in == 0xFF

        with vsc.implies( self.data_type == DATA_OTHER ):
            self.data_in != 0
            self.data_in != 0xFF

def make_key( transaction ):
    if int( transaction.key_type ) == ONE_BIT_OFF:
        return EXPECTED_KEY ^ ( 1 << int( transaction.flip_bit ) )

    return ( int( transaction.key_high ) << 16 ) | int( transaction.key_low )

def get_data_type( data_in ):
    if data_in == 0:
        return "zero"

    if data_in == 0xFF:
        return "ones"

    return "other"

def pick_key_type( key_type, data_type, unlocked, did_reset ):
    return key_type

def pick_data_type( key_type, data_type, unlocked, did_reset ):
    return data_type

def pick_unlocked( key_type, data_type, unlocked, did_reset ):
    return unlocked

def pick_did_reset( key_type, data_type, unlocked, did_reset ):
    return did_reset

@CoverPoint( "top.key_type", xf=pick_key_type, bins=KEY_TYPES )
@CoverPoint( "top.data_type", xf=pick_data_type, bins=DATA_TYPES )
@CoverPoint( "top.unlocked", xf=pick_unlocked, bins=[ 0, 1 ] )
@CoverPoint( "top.did_reset", xf=pick_did_reset, bins=[ 0, 1 ] )
@CoverCross( "top.key_type_x_data_type", items=[ "top.key_type", "top.data_type" ] )
@CoverCross( "top.did_reset_x_unlocked", items=[ "top.did_reset", "top.unlocked" ] )
def sample_coverage( key_type, data_type, unlocked, did_reset ):
    pass

async def reset( dut ):
    cocotb.start_soon( Clock( dut.clk, 10, units="ns" ).start( ) )

    dut.key.value = 0
    dut.data_in.value = 0
    dut.rst_n.value = 0

    for _ in range( 3 ):
        await RisingEdge( dut.clk )

    await FallingEdge( dut.clk )
    dut.rst_n.value = 1

async def driver( dut, key, data_in, rst_n ):
    await FallingEdge( dut.clk )

    dut.key.value = key
    dut.data_in.value = data_in & DW_MASK
    dut.rst_n.value = rst_n

    await Timer( 1, units="ns" )

def monitor( dut ):
    return int( dut.unlocked.value ), int( dut.data_out.value ), int( dut.access_count.value )

def expected_outputs( key, data_in ):
    if key == EXPECTED_KEY:
        return 1, data_in & DW_MASK

    return 0, 0

def expected_next_count( access_count, unlocked, rst_n ):
    if rst_n == 0:
        return 0

    if unlocked == 1:
        return ( access_count + 1 ) % 256

    return access_count

def scoreboard( key, data_in, outputs, expected_count ):
    unlocked, data_out, access_count = outputs
    expected_unlocked, expected_data_out = expected_outputs( key, data_in )

    assert unlocked == expected_unlocked
    assert data_out == expected_data_out
    assert access_count == expected_count

@cocotb.test( )
async def test_random_keys( dut ):
    random.seed( SEED )
    await reset( dut )

    transaction = GateTransaction( )
    expected_count = 0

    for cycle in range( NUM_CYCLES ):
        transaction.randomize( )

        key = make_key( transaction )
        data_in = int( transaction.data_in )
        rst_n = 1 - int( transaction.do_reset )

        await driver( dut, key, data_in, rst_n )
        outputs = monitor( dut )
        scoreboard( key, data_in, outputs, expected_count )

        sample_coverage( KEY_TYPES[ int( transaction.key_type ) ], get_data_type( data_in ), outputs[ 0 ], int( transaction.do_reset ) )

        expected_unlocked, _ = expected_outputs( key, data_in )
        expected_count = expected_next_count( expected_count, expected_unlocked, rst_n )

        if ( cycle + 1 ) % 100 == 0:
            dut._log.info( f"cycle {cycle + 1} coverage {coverage_db[ 'top' ].cover_percentage:.1f}" )

    coverage_db.report_coverage( dut._log.info, bins=True )
    coverage_db.export_to_yaml( filename="coverage.yml" )

@cocotb.test( )
async def test_count_wrap( dut ):
    await reset( dut )
    expected_count = 0

    for _ in range( 300 ):
        await driver( dut, EXPECTED_KEY, 0x5A, 1 )
        scoreboard( EXPECTED_KEY, 0x5A, monitor( dut ), expected_count )
        expected_count = expected_next_count( expected_count, 1, 1 )

@cocotb.test( )
async def test_magic_key( dut ):
    await reset( dut )
    await driver( dut, 0xDEADBEEF, 0xAB, 1 )
    await RisingEdge( dut.clk )
    await Timer( 1, units="ns" )

    unlocked, data_out, access_count = monitor( dut )

    assert unlocked == 0
    assert data_out == 0