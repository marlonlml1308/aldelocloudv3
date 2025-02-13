<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('products', function (Blueprint $table) {
            $table->engine = 'InnoDB';
            $table->charset = 'utf8mb4';
            $table->collation = 'utf8mb4_unicode_ci';
            $table->id();
            $table->string('menuitemtext');
            $table->unsignedBigInteger('menucategoryid');
            $table->unsignedBigInteger('menugroupid');
            $table->integer('displayindex');
            $table->decimal('defaultunitprice',total: 10, places: 2);
            $table->boolean('menuiteminactive',false);
            $table->boolean('menuiteminstock',true);
            $table->boolean('menuitemtaxable',false);
            $table->boolean('gstapplied',false);
            $table->boolean('liquortaxapplied',false);
            $table->string('gaspump');
            $table->boolean('bar',true);
            $table->string('menuitemtype');
            $table->string('barcode');
            $table->decimal('dineinprice',total: 10, places: 2);
            $table->decimal('takeoutprice',total: 10, places: 2);
            $table->decimal('drivethruprice',total: 10, places: 2);
            $table->decimal('DeliveryPrice',total: 10, places: 2);
            $table->boolean('orderbyweight',false);
            $table->integer('qtycountdown');
            $table->timestamps();
            $table->foreign('menucategoryid')->references('id')->on('categories');
            $table->foreign('menugroupid')->references('id')->on('groups');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('products');
    }
};
