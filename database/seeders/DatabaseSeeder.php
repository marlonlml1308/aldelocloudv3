<?php

namespace Database\Seeders;

use App\Models\Branch;
use App\Models\Modules;
use App\Models\Role;
use App\Models\Taxes;
use App\Models\User;
// use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Spatie\Permission\Models\Role as ModelsRole;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        User::factory(10)->create();

        User::factory()->create([
            'name' => 'Test User',
            'email' => 'test@example.com',
        ]);

        $branch = new Branch();
        $branch->branch = 'PASTAIO CHIA';
        $branch->save();

        $branch = new Branch();
        $branch->branch = 'PASTAIO 125';
        $branch->save();

        $branch = new Branch();
        $branch->branch = 'PASTAIO COLINA';
        $branch->save();

        $branch = new Branch();
        $branch->branch = 'PASTAIO 140';
        $branch->save();

        $taxes = new Taxes();
        $taxes->taxname = 'IMPOCONSUMO 8%';
        $taxes->taxpercent = 8;
        $taxes->save();

        $taxes = new Taxes();
        $taxes->taxname = 'IVA 19%';
        $taxes->taxpercent = 19;
        $taxes->save();

        $taxes = new Taxes();
        $taxes->taxname = 'IVA 5%';
        $taxes->taxpercent = 5;
        $taxes->save();

        $modules = new Modules();
        $modules->name = 'MESAS';
        $modules->save();

        $modules = new Modules();
        $modules->name = 'PARA LLEVAR';
        $modules->save();

        $modules = new Modules();
        $modules->name = 'RAPPI';
        $modules->save();

        $modules = new Modules();
        $modules->name = 'DOMICILIOS';
        $modules->save();

    }
}
